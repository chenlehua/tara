"""
Test Excel Generator with Sample Data
======================================

Test that the Excel generator correctly produces TARA analysis results
with sample data when no real data is available.
"""

import asyncio
import sys
import os

# Add the backend path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'report-service'))

from app.generators.excel_generator import ExcelGenerator


async def test_excel_generation_with_empty_data():
    """Test Excel generation with empty data (should use sample data)."""
    generator = ExcelGenerator()
    
    # Test with minimal/empty data
    data = {
        "content": {
            "project": {
                "name": "测试项目",
                "description": "这是一个测试项目",
                "vehicle_type": "乘用车",
            },
            "assets": [],
            "threats": [],
            "control_measures": [],
            "risk_distribution": {},
        }
    }
    
    # Generate Excel
    buffer = await generator.generate(data, template="iso21434")
    
    # Check that the buffer has content
    assert buffer is not None
    assert buffer.getbuffer().nbytes > 0, "Generated Excel file should not be empty"
    
    # Save the file for inspection
    output_path = os.path.join(os.path.dirname(__file__), "output", "test_tara_report_sample.xlsx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"✓ Excel file generated successfully: {output_path}")
    print(f"  File size: {buffer.getbuffer().nbytes} bytes")
    return True


async def test_excel_generation_with_real_data():
    """Test Excel generation with provided data."""
    generator = ExcelGenerator()
    
    # Test with real data structure
    data = {
        "content": {
            "project": {
                "name": "车载IVI系统安全分析",
                "description": "针对高端乘用车车载信息娱乐系统的TARA分析",
                "vehicle_type": "高端乘用车",
                "standard": "ISO/SAE 21434",
            },
            "assets": [
                {
                    "id": 1,
                    "name": "主处理器SOC",
                    "asset_type": "ECU",
                    "category": "内部实体",
                    "description": "高通SA8155P处理器",
                    "security_attrs": {
                        "authenticity": True,
                        "integrity": True,
                        "confidentiality": True,
                        "availability": True,
                    },
                    "interfaces": [{"type": "Ethernet"}, {"type": "USB"}]
                },
                {
                    "id": 2,
                    "name": "WiFi模块",
                    "asset_type": "通信模块",
                    "category": "外部接口",
                    "description": "WiFi 6无线模块",
                    "security_attrs": {
                        "authenticity": True,
                        "integrity": True,
                        "confidentiality": True,
                        "availability": True,
                    },
                    "interfaces": [{"type": "WiFi"}]
                },
            ],
            "threats": [
                {
                    "id": 1,
                    "name": "远程代码执行攻击",
                    "threat_name": "远程代码执行攻击",
                    "threat_type": "E",
                    "description": "攻击者通过网络漏洞远程执行恶意代码",
                    "attack_vector": "Network远程网络",
                    "attack_path": "WiFi→SOC→系统",
                    "asset_id": 1,
                    "asset_name": "主处理器SOC",
                    "safety_impact": 4,
                    "financial_impact": 3,
                    "operational_impact": 4,
                    "privacy_impact": 3,
                    "impact_level": 4,
                    "risk_level": "CAL-4",
                    "wp29_ref": "4.3.5",
                    "iso_clause": "9.8",
                },
                {
                    "id": 2,
                    "name": "无线通信窃听",
                    "threat_name": "无线通信窃听",
                    "threat_type": "I",
                    "description": "攻击者窃听WiFi通信获取敏感信息",
                    "attack_vector": "Adjacent相邻网络",
                    "attack_path": "WiFi信号→数据窃取",
                    "asset_id": 2,
                    "asset_name": "WiFi模块",
                    "safety_impact": 0,
                    "financial_impact": 2,
                    "operational_impact": 1,
                    "privacy_impact": 4,
                    "impact_level": 4,
                    "risk_level": "CAL-3",
                    "wp29_ref": "4.3.3",
                    "iso_clause": "9.6",
                },
            ],
            "control_measures": [
                {
                    "id": 1,
                    "threat_id": 1,
                    "threat_risk_id": 1,
                    "name": "安全启动验证",
                    "implementation": "使用HSM验证固件签名",
                    "iso21434_ref": "RQ-09-01",
                },
                {
                    "id": 2,
                    "threat_id": 1,
                    "threat_risk_id": 1,
                    "name": "运行时保护",
                    "implementation": "启用ASLR和栈保护",
                    "iso21434_ref": "RQ-09-02",
                },
                {
                    "id": 3,
                    "threat_id": 2,
                    "threat_risk_id": 2,
                    "name": "通信加密",
                    "implementation": "使用WPA3加密WiFi通信",
                    "iso21434_ref": "RQ-09-03",
                },
            ],
            "risk_distribution": {
                "CAL-4": 1,
                "CAL-3": 1,
                "CAL-2": 0,
                "CAL-1": 0,
            },
        }
    }
    
    # Generate Excel
    buffer = await generator.generate(data, template="iso21434")
    
    # Check that the buffer has content
    assert buffer is not None
    assert buffer.getbuffer().nbytes > 0, "Generated Excel file should not be empty"
    
    # Save the file for inspection
    output_path = os.path.join(os.path.dirname(__file__), "output", "test_tara_report_real.xlsx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"✓ Excel file with real data generated successfully: {output_path}")
    print(f"  File size: {buffer.getbuffer().nbytes} bytes")
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Excel Generator for TARA Reports")
    print("=" * 60)
    
    try:
        # Test 1: Empty data (should use sample data)
        print("\n[Test 1] Testing with empty data (sample data generation)...")
        await test_excel_generation_with_empty_data()
        
        # Test 2: Real data
        print("\n[Test 2] Testing with real data...")
        await test_excel_generation_with_real_data()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
