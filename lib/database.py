import argon2
import pymongo
from bson.errors import InvalidId
from bson.objectid import ObjectId


class CDNDatabase:
    def __init__(self, mongo_uri, salt):
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client["cdn"]

        self.salt = salt

        # Collections
        self.users = self._db["users"]
        self.zones = self._db["zones"]
        self.nodes = self._db["nodes"]

    # User methods

    def _user_exists(self, user):
        """
        Check if a user exists
        :param user: User's document ID as string
        :return: True if user exists, False if not
        """

        # Check user doc validity
        try:
            user_id = ObjectId(user)
        except InvalidId:
            return False

        # If no user exists
        if not self.users.find_one({"_id": user_id}):
            return False

        return True

    def add_user(self, username, password):
        """
        Register a new user
        :param username: User's username
        :param password: User's plaintext password
        :return: error string, None if success
        """

        user_doc = self.users.find_one({"username": username})
        if user_doc is None:
            self.users.insert_one({
                "username": username,
                "password": argon2.argon2_hash(password, self.salt)
            })

            return None  # No error
        else:
            return "Account with this email already exists"

    def authenticated(self, username: str, password: str) -> str:
        """
        Validate user credentials and return user document ID
        :param username: Plaintext username
        :param password: Hashed password
        :return: user's document ID as string, "" if not authorized
        """

        user_doc = self.users.find_one({"username": username})
        if user_doc and (user_doc["password"] == argon2.argon2_hash(password, self.salt)):
            return str(user_doc["_id"])

        return ""  # Not authorized

    # End user methods
    # Start zone methods

    def zone_exists(self, zone):
        """
        Check if a zone exists
        :param zone: Zone as string
        :return: True if zone exists, False if not
        """

        # If no user exists
        if not self.zones.find_one({"zone": zone}):
            return False

        return True

    def add_zone(self, zone, user_id):
        """
        Add a zone
        :param zone: Zone in human form (example.com/2001:db8::1)
        :param user_id: User to authorize zone to (Document ID)
        :return: Error, None if no error
        """
        if zone and ("." in zone):
            if self._user_exists(user_id):
                user = ObjectId(user_id)
                if not self.zone_exists(zone):
                    # Create zone
                    new_zone = self.zones.insert_one({
                        "zone": zone,
                        "users": [user],
                        "records": [],
                        "serial": strftime("%Y%m%d%S")
                    })

                    # Update the user's document to include new zone
                    self.users.update_one({"_id": user}, {"$push": {"zones": new_zone.inserted_id}})

                    return None  # No error
                else:
                    return "Zone already exists"

            else:
                return "User doesn't exist"
        else:
            return "Invalid zone"

    def delete_zone(self, zone):
        """
        Delete a zone
        :param zone: Zone ID
        :return: Error, None if success
        """

        if self.zone_exists(zone):
            zone_doc = self.zones.find_one({"zone": zone})

            zone_users = zone_doc.get("users")
            if zone_users:
                for user in zone_users:
                    # Pull the zone doc out of the user's zones array
                    self.users.update_one({"_id": user}, {"$pull": {"zones": zone_doc["_id"]}})

            # Delete the zone itself
            self.zones.delete_one({"_id": zone_doc["_id"]})

            return None  # No error
        else:
            return "Zone doesn't exist"

    def get_zones(self, user_id: str) -> list:
        """
        Get all zones for a user
        :param user_id: User ID
        :return: list of authorized zones
        """

        authorized_zones = []

        if self._user_exists(user_id):
            user_doc = self.users.find_one({"_id": ObjectId(user_id)})
            user_zones = user_doc.get("zones")
            if user_zones:
                for zone_id in user_zones:
                    authorized_zones.append(self.zones.find_one({"_id": zone_id}))

        return authorized_zones

    # End zone methods
    # Start record methods

    def add_record(self, zone: str, domain: str, _type: str, value: str, ttl: str):
        """
        Add a record to a zone
        :param zone: Parent zone
        :param domain: Domain in BIND format
        :param _type: Record type
        :param value: Record value
        :param ttl: TTL
        :return:
        """

        if self.zone_exists(zone) and (zone and domain and _type and value and ttl):
            self.zones.update_one({"zone": zone}, {"$push": {"records": {
                "domain": domain,
                "type": _type,
                "value": value,
                "ttl": ttl
            }}})

            self.zones.update_one({"zone": zone}, {"$set": {"serial": strftime("%Y%m%d%S")}})
        else:
            return "Zone doesn't exist or entry is blank"

    def delete_record(self, zone, record_id):
        """
        Delete a record by id
        :param zone: Parent zone
        :param record_id:
        :return:
        """

        if self.zone_exists(zone):
            # Get current records
            current_records = self.zones.find_one({"zone": zone})["records"]

            # Remove the record
            current_records.pop(int(record_id))

            # Set the modified records
            self.zones.update_one({"zone": zone}, {"$set": {
                "records": current_record,
                "serial": strftime("%Y%m%d%S")
            }})

    # End record methods
    # Start node methods

    def get_nodes(self):
        return list(self.nodes.find())

    def add_node(self, uid: str, location: str, management: str, operational: bool):
        """
        Add a node
        :param uid: location-country_code. For example Fremont, California is fmt-us
        :param location: Full location, for example: Fremont, California
        :param management: Management IP address
        :param operational: Is the node operational?
        :return:
        """

        self.nodes.insert_one({
            "uid": uid,
            "location": location,
            "management": management,
            "operational": operational
        })

    # End node methods

    def authorized_for_zone(self, user_id, zone):
        """
        Is user authorized for zone?
        :param user_id:
        :param zone:
        :return:
        """
        if self._user_exists(user_id) and self.zone_exists(zone):
            zone_doc = self.zones.find_one({"zone": zone})
            return ObjectId(user_id) in zone_doc["users"]
        else:
            return False

    def get_zone(self, user, zone):
        if self.authorized_for_zone(user, zone):
            return self.zones.find_one({"zone": zone})
        else:
            return "Error: Zone not authorized"

    def get_all_zones(self):
        return self.zones.find({})

    def get_total_records(self, user: str) -> int:
        """
        Get total number of records that a user has
        :param user: User's id
        :return: number of records
        """
        total_records = 0
        if self._user_exists(user):
            for zone in self.get_zones(user):
                total_records += len(zone["records"])

        return total_records
