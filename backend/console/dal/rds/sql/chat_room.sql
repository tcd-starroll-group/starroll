DROP TABLE IF EXISTS `chat_rooms`;

CREATE TABLE chat_rooms (
    room_id VARCHAR(64) PRIMARY KEY COMMENT 'star HIP/GroupID',
    name VARCHAR(128) NOT NULL COMMENT 'GroupName/StarName',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'group activate/create time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='GroupChatRoomRawData';