@app.get("/health")
def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return {"status": "ok"} 