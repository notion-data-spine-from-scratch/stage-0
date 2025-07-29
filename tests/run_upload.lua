local token = os.getenv("TOKEN")
local key = os.getenv("KEY") or "test.txt"

if os.getenv("STUB_JWT") then
  package.loaded["resty.jwt"] = {
    verify = function(_, _, token)
      if token == "invalid" then
        return { verified = false }
      else
        return { verified = true }
      end
    end,
  }
end

ngx = {
  req = {
    read_body = function() end,
    get_headers = function()
      if token then
        return { ["Authorization"] = "Bearer " .. token }
      else
        return {}
      end
    end
  },
  var = { arg_key = key },
  exit = function(code) io.write("EXIT:"..code) os.exit(0) end,
  say = function(str) io.write(str) end,
  log = function() end
}

dofile("services/asset-proxy/lua/upload.lua")
