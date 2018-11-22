get_mysql_user_data = ''''''


get_user_password_query = '''SELECT u.password
  FROM user u
  WHERE u.chat_id = %s
  AND u.archive = 0
  ;'''

check_registration_query = '''SELECT u.chat_id
  FROM user u
  WHERE u.chat_id = %s
  AND u.archive = 0
  ;'''


get_menu_query = '''SELECT
  'main' AS menu_type,
  GROUP_CONCAT(m.button_name ORDER BY m.menu_order ASC SEPARATOR ';') AS button_name,
  GROUP_CONCAT(m.callback_data ORDER BY m.menu_order ASC SEPARATOR ';') AS callback_data,
  GROUP_CONCAT(IFNULL(m.message, 'UNDEFINED') ORDER BY m.menu_order ASC SEPARATOR ';') AS message
FROM user u
  JOIN user_menu_permission ump
    ON ump.chat_id = u.chat_id AND ump.archive = 0
  JOIN menu m
    ON m.id = ump.menu_id AND m.menu_level = 1 AND m.archive = 0
WHERE u.chat_id =  %(chat_id)s
AND u.archive = 0
UNION
SELECT
  m.menu_type AS menu_type,
  GROUP_CONCAT(m.button_name ORDER BY m.menu_order ASC SEPARATOR ';') AS button_name,
  GROUP_CONCAT(m.callback_data ORDER BY m.menu_order ASC SEPARATOR ';') AS callback_data,
  GROUP_CONCAT(IFNULL(m.message, 'UNDEFINED') ORDER BY m.menu_order ASC SEPARATOR ';') AS message
FROM user u
  JOIN user_menu_permission ump
    ON ump.chat_id = u.chat_id AND ump.archive = 0
  JOIN menu m
    ON m.id = ump.menu_id AND m.menu_level = 2 AND m.archive = 0
WHERE u.chat_id = %(chat_id)s
AND u.archive = 0
GROUP BY menu_type
;'''


get_help_query = '''SELECT
  GROUP_CONCAT(
  IF(m.menu_level=1,
  IF(m.help_string IS NULL, m.button_name, CONCAT(m.button_name, ' (', m.help_string, ')')),
  CONCAT('- ', IF(m.help_string IS NULL, m.button_name, CONCAT(m.button_name, '\n    ', m.help_string)))) ORDER BY m.menu_type, m.menu_level SEPARATOR '\n') AS help_data
FROM user u
  JOIN user_menu_permission ump
    ON ump.chat_id = u.chat_id AND ump.archive = 0
  JOIN menu m
    ON m.id = ump.menu_id AND m.archive = 0
WHERE u.chat_id = '%s'
AND u.archive = 0
 ORDER BY m.submenu_type, m.menu_level;'''
