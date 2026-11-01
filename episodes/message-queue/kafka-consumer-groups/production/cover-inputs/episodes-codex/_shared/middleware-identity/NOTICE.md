# Middleware identity artwork

Redis, Apache Kafka, and RabbitMQ icons are the unmodified original SVG artwork from Devicon, pinned to the commit and complete hashes in [source.json](source.json). The original MIT notice is retained in [LICENSE.txt](LICENSE.txt). Data URLs in icon-data.ts encode those exact SVG bytes; rendering does not fetch any network resource.

Redis, Apache Kafka, and RabbitMQ names and marks retain their respective owners and brand policies. This educational use identifies an implementation example; it does not claim official brand authorization, affiliation or endorsement. Redis is not synonymous with all cache implementations; Kafka is not synonymous with all messaging systems. RabbitMQ is available when the episode illustrates queue/manual acknowledgement and automatic redelivery behavior.

Use with the actual Chinese role label, such as `缓存 · Redis示例` or `消息中间件 · Kafka示例` / `消息队列 · RabbitMQ示例`. Do not mark browser/HTTP/CDN caches, ordinary messages, Outbox database rows, or another named message system as Redis/Kafka/RabbitMQ. The role and mechanism must be checked per episode before adoption.

Kafka's original dark artwork sits on a small pale backing for contrast on the dark canvas. The graphic's color and aspect ratio remain unchanged. Redis retains its original red artwork; RabbitMQ retains its original orange artwork. Neither mark changes with success/failure; data and request paths carry state colors.

## Component

`const MiddlewareMark = createMiddlewareIdentity(React);`

`<MiddlewareMark kind="redis" size={44}/>` / `<MiddlewareMark kind="kafka" size={44}/>` / `<MiddlewareMark kind="rabbitmq" size={44}/>` beside the role label. Keep the mark inside the same local/group opacity and camera transform as that role.
