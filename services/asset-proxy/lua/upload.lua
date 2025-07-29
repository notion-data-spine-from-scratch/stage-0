local cjson = require "cjson"
ngx.req.read_body()
local auth = ngx.req.get_headers()["Authorization"]
if not auth then
  ngx.exit(401)
end
-- here we would validate JWT and generate presigned URL
ngx.say(cjson.encode({ok=true}))
