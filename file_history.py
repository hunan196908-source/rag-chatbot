from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
import os
import json
from typing import Sequence


def get_history(session_id, storage_path="./path_history"):

    class FileHistoryMessageHistory(BaseChatMessageHistory):
        def __init__(self):
            self.session_id = session_id
            self.storage_path = storage_path
            self.file_path = os.path.join(self.storage_path, self.session_id)

            # 文件夹是否存在
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        def add_messages(self, messages: Sequence[BaseMessage]):
            all_messages = list(self.messages)   # 已有的消息列表
            all_messages.extend(messages)        # 新的和已有的合在一起

            new_messages = [message_to_dict(message) for message in all_messages]
            with open(self.file_path, 'w', encoding="utf-8") as f:
                json.dump(new_messages, f)

        @property
        def messages(self) -> list[BaseMessage]:
            try:
                with open(self.file_path, 'r', encoding="utf-8") as f:
                    messages_data = json.load(f)
                    return messages_from_dict(messages_data)
            except FileNotFoundError:
                return []

        def clear(self) -> None:
            with open(self.file_path, 'w', encoding="utf-8") as f:
                json.dump([], f)

    return FileHistoryMessageHistory()
