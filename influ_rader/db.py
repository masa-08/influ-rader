import json
from typing import Any, List, Optional

import firebase_admin
from error import DbInitializeError, DbOperationError
from firebase_admin import credentials, firestore
from loguru import logger
from requests import JSONDecodeError


class Db:
    def __init__(self, credential: str) -> None:
        try:
            info = self.__parse_credential_string(credential)
            cred = self.__initialize_credential(info)
            self.__initialize_firebase_app(cred)
            self.__initialize_firestore()
        except DbInitializeError:
            raise
        self.__collection = "influencers"

    def __parse_credential_string(self, credential: str) -> Any:
        try:
            info = json.loads(credential)
        except (JSONDecodeError, TypeError):
            logger.exception("Failed to parse json string credential")
            raise DbInitializeError
        return info

    def __initialize_credential(self, credential_info: Any) -> credentials.Certificate:
        try:
            cred = credentials.Certificate(credential_info)
        except (IOError, ValueError):
            logger.exception("Failed to initializes a credential from a Google service account certificate")
            raise DbInitializeError
        return cred

    def __initialize_firebase_app(self, credential: credentials.Certificate) -> None:
        try:
            firebase_admin.initialize_app(credential)
        except ValueError:
            logger.exception("Failed to initialize firebase app")
            raise DbInitializeError

    def __initialize_firestore(self) -> None:
        try:
            client = firestore.client()
        except ValueError:
            logger.exception("Failed to initialize firestore")
            raise DbInitializeError
        self.client = client

    def has_record(self, doc_id: str) -> bool:
        try:
            doc_ref = self.client.collection(self.__collection).document(doc_id)
            doc = doc_ref.get()
        except Exception:
            logger.exception("Failed to get a document")
            raise DbOperationError
        return True if doc.exists else False

    def get(self, doc_id: str) -> Optional[dict[str, Any]]:
        try:
            doc_ref = self.client.collection(self.__collection).document(doc_id)
            doc = doc_ref.get()
        except Exception:
            logger.exception("Failed to get a document")
            raise DbOperationError

        if not doc.exists:
            logger.warning(f"The document with id `{doc_id}` was not found")
            return None
        return doc.to_dict()

    def add(self, doc_id: str, data: dict[str, Any]) -> None:
        try:
            doc_ref = self.client.collection(self.__collection).document(doc_id)
            result = doc_ref.set(data)
        except Exception:
            logger.exception("Failed to save a document")
            raise DbOperationError
        if "update_time" not in result:
            logger.warning("Saving document might be failed")

    def update(self, doc_id: str, data: dict[str, Any]) -> None:
        pass

    def delete(self, doc_id: str) -> None:
        pass

    def add_to_array(self, doc_id: str, field_name: str, array: List[Any]) -> None:
        try:
            doc_ref = self.client.collection(self.__collection).document(doc_id)
            result = doc_ref.update({field_name: firestore.ArrayUnion(array)})
        except Exception:
            logger.exception("Failed to update array on the database")
            raise DbOperationError
        if "update_time" not in result:
            logger.warning("Saving document might be failed")

    def remove_from_array(self, doc_id: str, field_name: str, array: List[Any]) -> None:
        try:
            doc_ref = self.client.collection(self.__collection).document(doc_id)
            result = doc_ref.update({field_name: firestore.ArrayRemove(array)})
        except Exception:
            logger.exception("Failed to update array on the database")
            raise DbOperationError
        if "update_time" not in result:
            logger.warning("Saving document might be failed")
