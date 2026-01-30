import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.config import settings
    
    print("\n" + "="*50)
    print("Configuration Test")
    print("="*50)
    
    print(f"\n✅ Azure OpenAI Endpoint: {settings.AZURE_OPENAI_ENDPOINT[:30]}...")
    print(f"✅ API Key configured: {'*' * 20}{settings.AZURE_OPENAI_API_KEY[-4:]}")
    print(f"✅ Deployment Name: {settings.AZURE_OPENAI_DEPLOYMENT_NAME}")
    print(f"✅ Embedding Deployment: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
    print(f"✅ Secret Key configured: {'*' * 28}{settings.SECRET_KEY[-4:]}")
    print(f"✅ Database URL: {settings.DATABASE_URL}")
    print(f"✅ CORS Origins: {settings.CORS_ORIGINS}")
    
    print("\n" + "="*50)
    print("✅ All configuration loaded successfully!")
    print("="*50 + "\n")
    
except Exception as e:
    print("\n" + "="*50)
    print("❌ Configuration Error")
    print("="*50)
    print(f"\nError: {e}")
    print("\nPlease check your .env file configuration.")
    print("="*50 + "\n")
    sys.exit(1)