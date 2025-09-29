#!/usr/bin/env python3
"""
Test diretto della funzione generate_api_key_v2 nel database
"""
import asyncio
import asyncpg
import json

async def test_database_function_directly():
    """Testa direttamente la funzione nel database"""
    
    # Usa l'URL dal setup precedente (sostituisci con il tuo)
    database_url = "postgresql://social_trends_user:hM5MIzSqMlbCZrb8412qekjnnqmEVlnw@dpg-d3bs0qj7mgec73a02d20-a.frankfurt-postgres.render.com/social_trends_vmp7"
    
    print("🔍 Testing database function directly...")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Test 1: Query semplice
        print("1️⃣ Simple query test...")
        result = await conn.fetchval("SELECT 1")
        print(f"   Result: {result}")
        
        # Test 2: Verifica se la funzione esiste
        print("2️⃣ Check if function exists...")
        function_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM pg_proc p 
                JOIN pg_namespace n ON p.pronamespace = n.oid 
                WHERE n.nspname = 'public' AND p.proname = 'generate_api_key_v2'
            )
        """)
        print(f"   Function exists: {function_exists}")
        
        if function_exists:
            # Test 3: Chiama la funzione direttamente
            print("3️⃣ Call function directly...")
            try:
                func_result = await conn.fetchval(
                    "SELECT generate_api_key_v2($1, $2, $3)",
                    "direct_test@example.com", "free", "direct_test"
                )
                print(f"   Function result type: {type(func_result)}")
                print(f"   Function result: {func_result}")
                
                if func_result:
                    try:
                        parsed = json.loads(func_result) if isinstance(func_result, str) else func_result
                        print(f"   Parsed JSON: {parsed}")
                    except Exception as e:
                        print(f"   JSON parse error: {e}")
                else:
                    print("   ❌ Function returned None/NULL")
                    
            except Exception as e:
                print(f"   ❌ Function call error: {e}")
        else:
            print("   ❌ Function does not exist!")
        
        # Test 4: Lista tutte le funzioni disponibili
        print("4️⃣ Available functions...")
        functions = await conn.fetch("""
            SELECT p.proname, pg_catalog.pg_get_function_result(p.oid) as result_type
            FROM pg_proc p 
            JOIN pg_namespace n ON p.pronamespace = n.oid 
            WHERE n.nspname = 'public' AND p.proname LIKE '%generate%'
        """)
        
        for func in functions:
            print(f"   - {func['proname']} -> {func['result_type']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_database_function_directly())