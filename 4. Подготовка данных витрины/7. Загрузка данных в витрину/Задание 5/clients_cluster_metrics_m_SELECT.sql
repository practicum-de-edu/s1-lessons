with act_lg as (
	select date_trunc('month',hitdatetime)::date "month",
		client_id,
		count(1) total_events,
		count(case when "action" = 'visit' then 1 end) visit_events,
		count(case when "action" = 'registration' then 1 end) registration_events,
		count(case when "action" = 'login' then 1 end) login_events,
		count(case when ("action" = 'login') and (prev_action = 'visit') then 1 end) visit_to_login_events
	from (
		select *,
			lag("action") over (partition by client_id order by hitdatetime) prev_action
		from user_activity_log
		where extract(year from hitdatetime) = 2021
			and "action" != 'N/A'
		)t
	group by 1,2
	),
pmnts as (
	select date_trunc('month',hitdatetime)::date "month",
		client_id,
		count(1) total_pay_events,
		count(case when "action" = 'accept-method' then 1 end) accepted_method_actions,
		count(case when "action" = 'make-payment' then 1 end) made_payments,
		avg(case when "action" = 'make-payment' then coalesce(payment_amount,0) else 0 end) avg_payment,
		sum(case when "action" = 'make-payment' then coalesce(payment_amount,0) else 0 end) sum_payments,
		sum(case when "action" = 'reject-payment' then coalesce(payment_amount,0) else 0 end)
			/ nullif(sum(case when "action" = 'make-payment' then coalesce(payment_amount,0) else 0 end),0) rejects_share
	from user_payment_log
	where extract(year from hitdatetime) = 2021
	group by 1,2
),
cntct as (
SELECT DISTINCT ON (client_id) client_id,
	SUBSTR(REGEXP_REPLACE(phone,'[^0123456789]','','g'),2,3) AS reg_code
FROM user_contacts
ORDER BY client_id,created_at DESC 
)
select coalesce(a."month",p."month") "month",
	ua.client_id,
	ua.utm_campaign,
	c.reg_code,
	coalesce(a.total_events,0) total_events,
	coalesce(a.visit_events,0) visit_events,
	coalesce(a.registration_events,0) registration_events,
	coalesce(a.login_events,0) login_events,
	coalesce(a.visit_to_login_events,0) visit_to_login_events,
	coalesce(p.total_pay_events,0) total_pay_events,
	coalesce(p.accepted_method_actions,0) accepted_method_actions,
	coalesce(p.avg_payment,0) avg_payment,
	coalesce(p.made_payments,0) made_payments,
	coalesce(p.sum_payments,0) sum_payments,
	p.rejects_share
from act_lg a
full join pmnts p on p."month" = a."month"
				and p.client_id = a.client_id
join user_attributes ua on ua.client_id = coalesce(a.client_id,p.client_id)
left join cntct c on c.client_id = ua.client_id
order by 1,2;