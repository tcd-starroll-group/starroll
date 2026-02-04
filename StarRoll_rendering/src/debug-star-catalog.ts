/**
 * 调试工具：测试星表数据加载
 * 在浏览器控制台运行此脚本以测试数据加载
 */

// 测试加载星表数据
export async function testStarCatalogLoading() {
    console.log('🔍 开始测试星表数据加载...');
    
    try {
        // 1. 测试 JSON 文件是否可访问
        console.log('📂 测试 JSON 文件访问...');
        const response = await fetch('/data/star-catalog/star-catalog.json');
        console.log('✅ 响应状态:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`HTTP 错误: ${response.status}`);
        }
        
        // 2. 解析 JSON
        console.log('📊 解析 JSON 数据...');
        const data = await response.json();
        console.log('✅ JSON 解析成功');
        console.log('📈 数据统计:');
        console.log('  - 总恒星数:', data.length);
        console.log('  - 第一颗恒星:', data[0]);
        console.log('  - 星等范围:', {
            min: Math.min(...data.map((s: any) => s.mag)),
            max: Math.max(...data.map((s: any) => s.mag))
        });
        
        // 3. 过滤可见恒星
        const visibleStars = data.filter((s: any) => s.mag <= 6.5);
        console.log('  - 可见恒星 (mag ≤ 6.5):', visibleStars.length);
        
        return { success: true, totalStars: data.length, visibleStars: visibleStars.length };
        
    } catch (error) {
        console.error('❌ 加载失败:', error);
        return { success: false, error };
    }
}

// 在浏览器控制台可以调用
if (typeof window !== 'undefined') {
    (window as any).testStarCatalog = testStarCatalogLoading;
    console.log('💡 提示：在控制台运行 testStarCatalog() 来测试星表加载');
}
