from pyngrok import ngrok

# 关闭所有现存的隧道
ngrok.kill()

# 重新启动你需要的隧道
public_url = ngrok.connect(5000)
print(f"ngrok tunnel 'http://{public_url}' -> 'http://127.0.0.1:5000'")
