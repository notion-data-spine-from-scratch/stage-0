local cjson = require "cjson"
local jwt = require "resty.jwt"

ngx.req.read_body()
local auth = ngx.req.get_headers()["Authorization"]
if not auth then
  return ngx.exit(401)
end

local token = auth:match("Bearer%s+(.+)")
if not token then
  return ngx.exit(401)
end

local secret = os.getenv("JWT_SECRET") or "secret"
local verified = jwt:verify(secret, token)
if not verified["verified"] then
  return ngx.exit(401)
end

local key = ngx.var.arg_key
if not key then
  return ngx.exit(401)
end

local presign_path = os.getenv("PRESIGN_PATH") or "/usr/local/bin/presign.py"
local handle = io.popen("python3 " .. presign_path .. " " .. key)
local url = handle:read("*a")
handle:close()
url = url:gsub("%s+$", "")

ngx.say(cjson.encode({url = url}))
