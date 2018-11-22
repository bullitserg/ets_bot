get_request_ds_status_info_query = '''SELECT
  last_do.inn AS inn,
  DATE_ADD(last_do.max_date, INTERVAL 3 HOUR) AS operation_datetime,
  p.amount AS amount,
  p.bank_id AS bank_code,
  CASE p.status
  WHEN -30 THEN IF(p.type = 'block', 'Проблемная блокировка', IF(p.type = 'release', 'Проблемное разблокирование', IF(p.type = 'commission', 'Проблемное списание комиссии', '-')))
  WHEN -10 THEN IF(p.type = 'block', 'Проблемная блокировка', IF(p.type = 'release', 'Проблемное разблокирование', IF(p.type = 'commission', 'Проблемное списание комиссии', '-')))
  WHEN 0 THEN IF(p.type = 'block', 'Статус блокировки неизвестен', IF(p.type = 'release', 'Статус разблокировки неизвестен', IF(p.type = 'commission', 'Статус списания комиссии неизвестен', '-')))
  WHEN 1 THEN IF(p.type = 'block', 'Заблокировано', IF(p.type = 'release', 'Разблокировано', IF(p.type = 'commission', 'Списана комиссия', '-')))
  WHEN 2 THEN IF(p.type = 'block', 'Не заблокировано', IF(p.type = 'release', 'Не разблокировано', IF(p.type = 'commission', 'Ошибка списания комиссии', '-')))
  END AS operation_status_text,
  IF(p.status IN (2, -10, -30), p.description, NULL) AS description_text,
  p.status AS operation_status_id,
  p.guid AS guid
  FROM
  (
SELECT
  p.inn,
  MAX(p.exchange_date) AS max_date
FROM payment p
WHERE p.type IN ('release', 'block')
  AND p.purchase_number = '%s' %s
GROUP BY p.inn
) AS last_do
JOIN payment p ON p.inn = last_do.inn AND p.exchange_date = last_do.max_date
ORDER BY p.type, last_do.max_date DESC
;'''


check_operation_status_by_guid_query = '''SELECT
  CONCAT(
  'Процедура: ', p.purchase_number,
  '\nЗаявка: ', p.request_id,
  '\nИНН: ', p.inn,
  '\nКПП: ', IFNULL(p.kpp, '-'),
  '\nБанк: ', CONCAT(b.name, ' (', p.bank_id, ')'),
  '\nСчет: ', p.account,
  '\nСумма: ', p.amount,
  '\nДата отправки: ', DATE_ADD(p.exchange_date, INTERVAL 3 HOUR),
  '\nДата ответа: ', IFNULL(DATE_ADD(p.response_date, INTERVAL 3 HOUR), '-'),
  '\nСтатус: ', CONCAT_WS(', ', CONCAT(CASE p.status
  WHEN -30 THEN IF(p.type = 'block', 'Проблемная блокировка', IF(p.type = 'release', 'Проблемное разблокирование', IF(p.type = 'commission', 'Проблемное списание комиссии', '-')))
  WHEN -10 THEN IF(p.type = 'block', 'Проблемная блокировка', IF(p.type = 'release', 'Проблемное разблокирование', IF(p.type = 'commission', 'Проблемное списание комиссии', '-')))
  WHEN 0 THEN IF(p.type = 'block', 'Статус блокировки неизвестен', IF(p.type = 'release', 'Статус разблокировки неизвестен', IF(p.type = 'commission', 'Статус списания комиссии неизвестен', '-')))
  WHEN 1 THEN IF(p.type = 'block', 'Заблокировано', IF(p.type = 'release', 'Разблокировано', IF(p.type = 'commission', 'Списана комиссия', '-')))
  WHEN 2 THEN IF(p.type = 'block', 'Не заблокировано', IF(p.type = 'release', 'Не разблокировано', IF(p.type = 'commission', 'Ошибка списания комиссии', '-')))
  END, ' (код ', p.status, ')'), IF(p.status IN (2, -10, -30), p.description, ''))) AS info
FROM payment p
JOIN bank b ON b.code = p.bank_id
WHERE p.guid = 'CD2AF24B8D818F32606206156F8EB71D'
;'''