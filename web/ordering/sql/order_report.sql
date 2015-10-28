select count(o.orderid) "Total Orders",
    SUM(case when o.status = 'complete' then 1 else 0 end) "Complete",
    SUM(case when o.status = 'ordered' then 1 else 0 end) "Open",
    u.email,
    u.first_name,
    u.last_name
    FROM 
         ordering_order o,
         auth_user u
    WHERE o.user_id = u.id 
    AND o.status != 'purged'
    GROUP BY u.email,
             u.first_name,
             u.last_name
        
    ORDER BY "Total Orders" DESC;
