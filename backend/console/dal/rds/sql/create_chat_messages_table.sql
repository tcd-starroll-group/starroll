DROP TABLE IF EXISTS `chat_messages`;
CREATE TABLE `chat_messages`
(
    `id`           bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'User ID (Primary Key)',
    `user_id`      bigint(20) unsigned NOT NULL COMMENT 'user id of the sender',
    `chatroom_id`  bigint(20) unsigned NOT NULL COMMENT 'chatroom id',
    `message_id`   bigint(20) unsigned NOT NULL COMMENT 'message snowflake id',
    `message`      TEXT                NOT NULL COMMENT 'message content',
    `created_at`   timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_chatroom_message` (`chatroom_id`, `message_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Chat messgaes table';