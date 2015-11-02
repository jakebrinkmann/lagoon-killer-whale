select distinct o.orderid, count(s.name) from ordering_order o, ordering_scene s where o.id = s.order_id and s.status = 'error' group by o.orderid;
