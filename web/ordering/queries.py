

def list_all_orders(email=None, username=None):
            ''' This is FAR more efficient.
        select u.username, s.order_id, o.orderid, o.order_date "date ordered", o.status "order status", count(s.name) TOTAL, count(comp.number) complete from ordering_order o, ordering_scene s, auth_user u, (select order_id , count(*) number from ordering_scene where status IN ('complete', 'order') group by order_id) comp where s.order_id = comp.order_id and o.id = s.order_id and u.id = o.user_id  group by s.order_id, o.orderid, u.username, o.order_date, o.status order by u.username, o.order_date offset 40 limit 10
        '''
    query = '''
        SELECT 
            u.username,
            s.order_id,
            o.orderid,
            o.order_date,
            o.status,
            count(s.name) total,
            count(comp.number) complete,
        FROM
            ordering_order o,
            ordering_scene s,
            auth_user u,
            (SELECT 
                order_id, 
                count(*) number,
             FROM
                ordering_scene 
             WHERE 
                status IN ('complete', 'unavailable')
             GROUP BY order_id
            ) comp
        WHERE
            s.order_id = comp.order_id AND
            o.id = s.order_id AND
            u.id = o.user_id
        GROUP BY
            s.order_id,
            o.orderid,
            u.username,
            o.order_date,
            o.status
        ORDER BY
            u.username,
            o.order_date
        OFFSET 40
        LIMIT 10;                    
    '''

