# Api Design


## Resource URL

### todo model for demo

| HTTP 方法   |  行为          |         示例 |
| ---------- |-------------- |---------------|
| GET      |   获取资源的信息 |    http://tecstack.org/demo/api/v1.0/todos |
| GET      |   获取某个特定资源的信息 | http://tecstack.org/demo/api/v1.0/todos/123 |
| POST     |   创建新资源           |  http://tecstack.org/demo/api/v1.0/todos |
| PUT      |   更新资源             |  http://tecstack.org/demo/api/v1.0/todos/123 |
| DELETE   |   删除资源             |  http://tecstack.org/demo/api/v1.0/todos/123 |

### Biz Model

This is for orders, products, payment... mgmt.

| HTTP 方法   |  行为          |         示例 |
| ---------- |-------------- |---------------|
| GET      |   获取资源的信息 |    http://tecstack.org/biz/api/v1.0/orders |
| GET      |   获取某个特定资源的信息 | http://tecstack.org/biz/api/v1.0/orders/123 |
| POST     |   创建新资源           |  http://tecstack.org/biz/api/v1.0/orders |
| PUT      |   更新资源             |  http://tecstack.org/biz/api/v1.0/orders/123 |
| DELETE   |   删除资源             |  http://tecstack.org/biz/api/v1.0/orders/123 |

### Crm Model

This is for customer, company, ... mgmt.

| HTTP 方法   |  行为          |         示例 |
| ---------- |-------------- |---------------|
| GET      |   获取资源的信息 |    http://tecstack.org/crm/api/v1.0/customers |
| GET      |   获取某个特定资源的信息 | http://tecstack.org/crm/api/v1.0/customers/123 |
| POST     |   创建新资源           |  http://tecstack.org/crm/api/v1.0/customers |
| PUT      |   更新资源             |  http://tecstack.org/crm/api/v1.0/customers/123 |
| DELETE   |   删除资源             |  http://tecstack.org/crm/api/v1.0/customers/123 |

### ... other Models

TBD.


## Authentication

TBD.
