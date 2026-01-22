CREATE TABLE `user`
(
	`id`                     bigint       NOT NULL AUTO_INCREMENT COMMENT 'ID',
	`name`                   varchar(256) NOT NULL COMMENT 'user name',
	`password`               varchar(256) NOT NULL COMMENT 'hash of user password',
	`email`                  varchar(256) NOT NULL COMMENT 'Email',
	PRIMARY KEY (`id`),
	KEY `idx_name` (`name`)
) ENGINE = InnoDB
  CHARSET = utf8mb4;