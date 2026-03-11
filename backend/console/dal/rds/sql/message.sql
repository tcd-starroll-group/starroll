DROP TABLE IF EXISTS `chat_messages`;

CREATE TABLE chat_messages (
    id BIGINT PRIMARY KEY COMMENT 'Snowflake ID',
    room_id VARCHAR(64) NOT NULL COMMENT 'HIP/groupchat ID',
    sender_id BIGINT NOT NULL COMMENT 'UserID',
    content TEXT NOT NULL COMMENT 'message or media URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'create time',
    INDEX idx_room_msg (room_id, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='history message';