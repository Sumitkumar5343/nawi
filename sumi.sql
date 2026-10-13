create database salesDB;
show databases;
use salesDB;
create table Salesman(Salesman_id int primary key, Salesman_name varchar(20) not null, City varchar(30), Commission  float);
insert into Salesman values
(5001, 'James', 'New york', 0.15),
(5002, 'Nandini', 'Delhi', 0.13),
(5003, 'Amit', 'Mumbai', 0.12),
(5004, 'Priya', 'Delhi', 0.14),
(5005, 'Rahul', 'Mumbai', 0.10),
(5006, 'Neha', 'Bhopal', 0.11);
select * from Salesman;
create table Customer( Customer_id int primary key, Customer_name varchar(20) not null, City Varchar(30), Grade int, Salesman_id int, foreign key (Salesman_id) references Salesman(Salesman_id));
insert into Customer values
(3001,'Ravi', 'Delhi', 2, 5002),
(3002,'Anita', 'Mumbai', 3, 5003),
(3003,'Suresh', 'Delhi', 1, 5002),
(3004,'Meena', 'Bhopal', 2, 5006),
(3005,'Karan', 'Mumbai', 3, 5005),
(3006,'Pooja', 'New york', 2, 5001),
(3007,'Arjun', 'Delhi', 3, 5004),
(3008,'Neha', 'Bhopal', 1, 5006),
(3009,'Rohit', 'Mumbai', 2, 5003),
(3010,'Sneha', 'Delhi', 3, 5004);
select * from Customer;
create table Orders (Order_id int primary key, Order_date date, Amount Float, Customer_id int, Salesman_id int, foreign key (Customer_id) references Customer(Customer_id), foreign key (Salesman_id) references Salesman(Salesman_id));
insert into Orders Values
(7001,'2026-01-10', 2500, 3001, 5002),
(7002,'2026-01-12', 1800, 3002, 5003),
(7003,'2026-01-15',3200, 3003, 5002),
(7004,'2026-01-18', 4500, 3004, 5006),
(7005,'2026-01-20', 1500, 3005, 5005),
(7006,'2026-01-22', 5200, 3006, 5001),
(7007,'2026-01-25', 2800, 3007, 5004),
(7008,'2026-02-02', 2100, 3008, 5006),
(7009,'2026-02-05', 3500, 3009, 5003),
(7010,'2026-02-08', 4200, 3010, 5004),
(7011,'2026-02-10', 3000, 3001, 5002),
(7012,'2026-02-12', 2700, 3002, 5003),
(7013,'2026-02-15', 1900, 3003, 5002),
(7014,'2026-02-18', 6000, 3004, 5006),
(7015,'2026-02-20', 2300, 3005, 5005),
(7016,'2026-02-22', 4800, 3007, 5004),
(7017,'2026-02-25', 1600, 3009, 5003),
(7018,'2026-02-28', 5500, 3010, 5004);
select * from Orders;
select count(Customer_id) from Customer;
select count(Salesman_id) from Salesman;
select count(Order_id) from Orders;
select sum(Amount) as TOTAL_SALES_AMOUNT from Orders;
select avg(Amount) as AVERAGE_ORDER_AMOUNT from Orders;
select max(Amount) from Orders;
select min(Amount) from Orders;
select sum(Commission) as TOTAL_COMMISsION from Salesman;
select City, count(*) as TOTAL_COSTUMERS from Customer Group by city;
select City, count(*) as TOTAL_SALESMAN from Salesman Group by city;
select Salesman_id, sum(Amount) as TOTAL_AMOUNT from Orders Group by Salesman_id;
select Salesman_id, avg(Amount) as AVERAGE_AMOUNT from Orders Group by Salesman_id;
select Salesman_id, count(*) as TOTAL_ORDERS from Orders Group by Salesman_id;
select Customer_id, sum(Amount) as TOTAL_AMOUNT from Orders Group by Customer_id;
select Customer_id, count(*) as TOTAL_ORDERS from Orders Group by Customer_id;
select Salesman_id, max(Amount) as TOTAL_AMOUNT from Orders Group by Salesman_id;
select Salesman_id, min(Amount) as TOTAL_AMOUNT from Orders Group by Salesman_id;
select Salesman_id, sum(Amount) as TOTAL_AMOUNT from Orders Group by Salesman_id having sum(Amount) > 10000;
select Salesman_id, count(*) as TOTAL_ORDERS from Orders Group by Salesman_id having count(*) > 2;
select Customer_id, count(*) as TOTAL_ORDERS from Orders Group by Customer_id having count(*) > 1;
select Customer_id, sum(Amount) as TOTAL_AMOUNT from Orders Group by Customer_id having sum(Amount) > 5000;
select City, count(*) as TOTAL_CUSTOMER from Customer group by city having count(*) > 2;
select Salesman_id, avg(Amount) as AVERAGE_AMOUNT from Orders Group by Salesman_id having avg(Amount) > 2500;
select Salesman_id, max(Amount) as MAXIMUM_AMOUNT from Orders Group by Salesman_id having max(Amount) > 5000;
