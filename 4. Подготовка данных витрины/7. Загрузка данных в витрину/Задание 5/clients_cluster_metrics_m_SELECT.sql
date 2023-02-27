WITH activity_stats AS (
    SELECT
        date_trunc('month', hitdatetime)::date                                          AS "month",
        client_id                                                                       AS client_id,
        COUNT(1)                                                                        AS total_events,
        SUM(CASE WHEN "action" = 'visit' THEN 1 ELSE 0 END)                             AS visit_events,
        SUM(CASE WHEN "action" = 'registration' THEN 1 ELSE 0 END)                      AS registration_events,
        SUM(CASE WHEN "action" = 'login' THEN 1 ELSE 0 END)                             AS login_events,
        SUM(CASE WHEN "action" = 'login' AND prev_action = 'visit' THEN 1 ELSE 0 END)   AS visit_to_login_events
    FROM (
        SELECT
            *,
            LAG("action") OVER (PARTITION BY client_id ORDER BY hitdatetime ASC) AS prev_action
        FROM user_activity_log
        WHERE
            extract(year FROM hitdatetime) = 2021
            AND "action" != 'N/A'
        ) AS t
    GROUP BY 1,2
),
payment_stats AS (
    SELECT
        date_trunc('month',hitdatetime)::date AS "month",
        client_id AS client_id,
        count(1) AS total_pay_events,
        count(CASE WHEN "action" = 'accept-method' THEN 1 END) AS accepted_method_actions,
        count(CASE WHEN "action" = 'make-payment' THEN 1 END) AS made_payments,
        avg(CASE WHEN "action" = 'make-payment' THEN coalesce(payment_amount,0) ELSE 0 END) AS avg_payment,
        sum(CASE WHEN "action" = 'make-payment' THEN coalesce(payment_amount,0) ELSE 0 END) AS sum_payments,
        sum(CASE WHEN "action" = 'reject-payment' THEN coalesce(payment_amount, 0) ELSE 0 END)
            / nullif(sum(CASE WHEN "action" = 'make-payment' THEN coalesce(payment_amount,0) ELSE 0 END), 0)    AS rejects_share
    FROM user_payment_log
    WHERE extract(year FROM hitdatetime) = 2021
    GROUP BY 1,2
),
user_contacts_latest AS (
    SELECT DISTINCT ON (client_id)
        client_id,
	    SUBSTR(REGEXP_REPLACE(phone,'[^0123456789]','','g'),2,3) AS reg_code
    FROM user_contacts
    ORDER BY client_id ASC, created_at DESC
)
SELECT
    coalesce(a."month", p."month")          AS "month",
    ua.client_id                            AS client_id,
    ua.utm_campaign                         AS utm_campaign,
    contacts.reg_code                       AS reg_code,
    coalesce(a.total_events,0)              AS total_events,
    coalesce(a.visit_events,0)              AS visit_events,
    coalesce(a.registration_events, 0)      AS registration_events,
    coalesce(a.login_events, 0)             AS login_events,
    coalesce(a.visit_to_login_events, 0)    AS visit_to_login_events,
    coalesce(p.total_pay_events, 0)         AS total_pay_events,
    coalesce(p.accepted_method_actions, 0)  AS accepted_method_actions,
    coalesce(p.avg_payment, 0)              AS avg_payment,
    coalesce(p.made_payments, 0)            AS made_payments,
    coalesce(p.sum_payments, 0)             AS sum_payments,
    p.rejects_share                         AS rejects_share
FROM activity_stats AS a
    FULL JOIN payment_stats AS p
        ON p."month" = a."month" AND p.client_id = a.client_id
    RIGHT JOIN user_attributes AS ua
        ON ua.client_id = coalesce(a.client_id, p.client_id)
    LEFT JOIN user_contacts_latest AS contacts
        ON contacts.client_id = ua.client_id
ORDER BY 1,2;