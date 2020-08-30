import argon2
import pymongo
from bson.errors import InvalidId
from bson.objectid import ObjectId

from config import configuration


class CDNDatabase:
    def __init__(self, mongo_uri):
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client["cdn"]

        # Collections
        self.users = self._db["users"]
        self.zones = self._db["zones"]
        self.servers = self._db["servers"]

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
                "password": argon2.argon2_hash(password, configuration.salt)
            })

            return None  # No error
        else:
            return "Account with this email already exists"

    def authenticated(self, username, password):
        """
        Validate user credentials and return user document ID
        :param username: Plaintext username
        :param password: Hashed password
        :return: user's document ID as string, None if not authorized
        """

        user_doc = self.users.find_one({"username": username})
        if user_doc and user_doc["password"] == argon2.argon2_hash(password, configuration.salt):
            return user_doc["_id"]

        return None  # Not authorized

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

        if self._user_exists(user_id):
            user = ObjectId(user_id)
            if not self.zone_exists(zone):
                # Create zone
                new_zone = self.zones.insert_one({
                    "zone": zone,
                    "users": [user],
                    "records": []
                })

                # Update the user's document to include new zone
                self.users.update_one({"_id": user}, {"$push": {"zones": new_zone.inserted_id}})

                return None  # No error
            else:
                return "Zone already exists"

        else:
            return "User doesn't exist"

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

    def authorized_for_zone(self, user_id, zone):
        user_id = ObjectId(user_id)

        userdoc = self.users.find_one({"_id": user_id})
        if not userdoc:
            return "ERROR: User not found."

        zonedoc = self.zones.find_one({"zone": zone})
        return user_id in zonedoc["users"]

    def get_zone(self, user, zone):
        if self.authorized_for_zone(user, zone):
            return self.zones.find_one({"zone": zone})
        else:
            return "Error: Zone not authorized"

    def get_all_zones(self):
        return self.zones.find({})

    def add_record(self, zone, domain, _type, value, ttl):
        self.zones.update_one({"zone": zone}, {"$push": {"records": {
            "domain": domain,
            "type": _type,
            "value": value,
            "ttl": ttl
        }}})

    def get_servers(self):
        return list(self.servers.find())

    def add_server(self, uid, location, transit, ixp, management, status):
        self.servers.insert_one({
            "uid": uid,
            "location": location,
            "transit": transit,
            "ixp": ixp,
            "management": management,
            "status": status
        })

    def delete_record(self, zone, record_id):
        current_records = self.zones.find_one({"zone": zone})["records"]
        current_records.pop(int(record_id))
        self.zones.update_one({"zone": zone}, {"$set": {"records": current_records}})
