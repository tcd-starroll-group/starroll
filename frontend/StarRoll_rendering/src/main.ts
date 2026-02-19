import { createApp } from 'vue';
import StarRollApp from './frameworks/vue/StarRollApp.vue';
import { initializeModels } from './config/models';
import { testStarCatalogLoading } from './debug-star-catalog';

// 初始化外部模型配置
initializeModels();

// 开发环境：测试星表加载
if (import.meta.env.DEV) {
    console.log('🌟 StarRoll V2 - 真实星表渲染系统');
    console.log('📊 运行测试...');
    testStarCatalogLoading().then(result => {
        if (result.success) {
            console.log('✅ 星表数据加载测试通过');
        }
    });
}

// 创建 Vue 应用实例
const app = createApp(StarRollApp);

// 挂载到 DOM
app.mount('#app');

