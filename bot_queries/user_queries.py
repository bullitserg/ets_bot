# ######################################### USER QUERIES ###########################################

reports_procedure_requests_query = '''SELECT
  p.publicationDateTime AS 'Дата публикации',
  p.registrationNumber AS 'Извещение ООС',
  p.name AS 'Наименование заказа',
  org.inn AS 'ИНН',
  org.fullName AS 'Наименование организатора',
  r.ordinalNumber AS '№ п/п',
  r.sendDateTime AS 'Дата подачи заявки',
  r.id AS 'Номер заявки',
  CONCAT(s.title, ', ', IF(cs.title IS NULL, '-', cs.title)) AS 'Статус заявки',
  o.inn AS 'ИНН участника',
  o.fullName AS 'Наименование участника'
FROM procedures p
  INNER JOIN procedureLot l
    ON p.id = l.procedureId
  INNER JOIN organization org
    ON org.id = p.customerId
  LEFT JOIN procedureRequest r
    ON p.id = r.procedureId AND l.id = r.lotId
  LEFT JOIN procedureStatus s
    ON s.id = r.requestStatusId
  LEFT JOIN procedureStatus cs
    ON cs.id = r.customerStatusId
  LEFT JOIN organization o
    ON o.id = r.organizationId
  LEFT JOIN procedureOffer po
    ON r.bestOfferId = po.id
WHERE p.registrationNumber IN ('%s')
AND p.archive = 0
AND p.actualId IS NULL
AND l.archive = 0
AND l.actualId IS NULL
ORDER BY p.registrationNumber, r.ordinalNumber, r.id
;'''


reports_fine_check_query = '''SELECT
  o.inn AS 'ИНН',
  o.kpp AS 'КПП',
  p.registrationNumber AS '№ извещения',
  pl.maxSum AS 'Начальная цена',
  ROUND(SUM(plc.provisionAmount), 2) AS 'Pазмер обеспечения заявки',
  ps.title AS 'Cтатус заявки (после подведения итогов)',
  pp.publicationDateTime AS 'Дата публикации протокола подведения итогов'
FROM procedureRequest pr
  INNER JOIN organization o
    ON o.id = pr.organizationId
  INNER JOIN procedureStatus ps
    ON ps.id = pr.customerStatusId
  INNER JOIN procedures p
    ON p.id = pr.procedureId
  INNER JOIN procedureLot pl
    ON pl.id = pr.lotId
  LEFT JOIN procedureLotCustomer plc
    ON plc.lotId = pr.lotId
  LEFT JOIN procedureProtocol pp
    ON pp.typeCode IN ('electronic.auction.protocol.request.final', 'electronic.auction.protocol.single.request.final') AND pp.procedureId = pr.procedureId
      LEFT JOIN procedureRequestResult rr ON pr.id = rr.requestId AND pp.id = rr.protocolId
  LEFT JOIN procedureRequestResultAdmittanceReason rrr ON rr.id = rrr.requestResultId
WHERE pp.publicationDateTime BETWEEN %s
AND p.actualId IS NULL
AND pr.actualId IS NULL
AND o.actualId IS NULL
AND pl.actualId IS NULL
AND plc.actualId IS NULL
AND pp.actualId IS NULL
AND p.archive = 0
AND pr.archive = 0
AND pl.archive = 0
AND o.inn = '%s'
AND o.active = 1
AND o.`type` = 'supplier'
AND pp.status = 24
AND p.procedureStatusId != 80
  AND rr.admittance = 0
  AND rrr.code IN ('request.nonconformity.unreliable.documents', 'request.nonconformity.unreliable.documents.update.20180701')
GROUP BY p.registrationNumber
ORDER BY pp.publicationDateTime
;'''


reports_user_exists_query = '''SELECT
  u.id
FROM user u
WHERE u.username = '%s'
;'''


reports_account_exists_query = '''SELECT GROUP_CONCAT(
  CONCAT(
  'ИНН: ', a.inn,
  '\nКПП: ', IFNULL(a.kpp, '-'),
  '\nНаименование организации: ', a.name,
  '\n№ счета: ', a.account_number,
  '\nНаименование банка: ', b.name,
  '\nДата обновления: ', DATE_FORMAT(a.update_time, '%%d.%%m.%%Y %%H:%%i:%%s')) SEPARATOR '\n----------------\n'
  ) AS info
FROM account a
  LEFT JOIN bank b
    ON b.id = a.bank_id
WHERE a.inn = '%s'
AND a.active = 1
  ;'''


report_inn_get_account_error_query = '''SELECT
  CONCAT_WS(' ','Банк:', b.name, '\nДата обработки:', ADDDATE(p.exchange_date, INTERVAL 3 HOUR)),
  p.document
  FROM package p
  JOIN bank b ON b.code = p.source
  WHERE p.id =
(SELECT
  MAX(p.id)
FROM package p
  JOIN bank b ON b.code = p.source
WHERE p.document LIKE '%%%s%%'
AND p.document_type IN ('PartyCheckRs', 'AccStatusNotifyRq'))
;'''
