import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import type { StarMeta } from '../../types/star-meta';

/**
 * 恒星名称标签管理器
 * 使用 CSS2D 在星星旁边显示名称
 */
export class StarLabelManager {
    private labelRenderer: CSS2DRenderer;
    private labels: Map<number, CSS2DObject> = new Map();
    private container: HTMLElement;
    
    // 常见亮星的中文名称
    private readonly BRIGHT_STAR_NAMES: { [hip: number]: string } = {
        // 猎户座
        27989: '参宿四 Betelgeuse',      // 猎户座α
        24436: '参宿七 Rigel',            // 猎户座β
        25336: '参宿五 Bellatrix',        // 猎户座γ
        26311: '参宿二 Alnilam',          // 猎户座ε
        26727: '参宿一 Alnitak',          // 猎户座ζ
        
        // 天鹅座
        102098: '天津四 Deneb',           // 天鹅座α
        100453: '天津一 Sadr',            // 天鹅座γ
        
        // 天鹰座
        97649: '牛郎星 Altair',           // 天鹰座α
        
        // 天琴座
        91262: '织女星 Vega',             // 天琴座α
        
        // 大角星
        69673: '大角星 Arcturus',         // 牧夫座α
        
        // 其他亮星
        32349: '天狼星 Sirius',           // 大犬座α
        30438: '南河三 Procyon',          // 小犬座α
        21421: '毕宿五 Aldebaran',        // 金牛座α
        113368: '北落师门 Fomalhaut',     // 南鱼座α
        
        // 北斗七星
        54061: '天枢',
        53910: '天璇',
        58001: '天玑',
        59774: '天权',
        62956: '玉衡',
        65378: '开阳',
        67301: '摇光',
        
        // 仙后座
        746: '王良一',
        3179: '王良二',
        4427: '王良三',
        6686: '王良四',
        8886: '王良五'
    };
    
    constructor(container: HTMLElement) {
        this.container = container;
        
        // 创建 CSS2D 渲染器
        this.labelRenderer = new CSS2DRenderer();
        this.labelRenderer.setSize(window.innerWidth, window.innerHeight);
        this.labelRenderer.domElement.style.position = 'absolute';
        this.labelRenderer.domElement.style.top = '0';
        this.labelRenderer.domElement.style.pointerEvents = 'none';
        container.appendChild(this.labelRenderer.domElement);
        
        // 监听窗口大小
        window.addEventListener('resize', this.onResize);
        
        console.log('🏷️ 星星标签管理器已初始化');
    }
    
    /**
     * 添加亮星标签
     * @param stars 星表数据
     * @param starPositions 星星的 3D 位置映射
     * @param magnitudeLimit 只显示这个星等以上的亮星
     */
    public addBrightStarLabels(
        starPositions: Map<number, THREE.Vector3>,
        magnitudeLimit: number = 2.5
    ): void {
        console.log(`🏷️ 添加亮星标签（星等 <= ${magnitudeLimit}）...`);
        
        let labelCount = 0;
        
        starPositions.forEach((position, hip) => {
            const name = this.BRIGHT_STAR_NAMES[hip];
            if (!name) return; // 只标注有名称的亮星
            
            // 创建标签元素
            const labelDiv = document.createElement('div');
            labelDiv.className = 'star-label';
            labelDiv.textContent = name;
            labelDiv.style.cssText = `
                color: rgba(255, 255, 255, 0.9);
                font-size: 11px;
                padding: 2px 6px;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 3px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                white-space: nowrap;
                pointer-events: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                backdrop-filter: blur(4px);
            `;
            
            const label = new CSS2DObject(labelDiv);
            label.position.copy(position);
            
            // 略微偏移避免遮挡星点
            label.position.multiplyScalar(1.01);
            
            this.labels.set(hip, label);
            labelCount++;
        });
        
        console.log(`✅ 添加了 ${labelCount} 个亮星标签`);
    }
    
    /**
     * 添加所有标签到场景
     */
    public addLabelsToScene(scene: THREE.Scene): void {
        this.labels.forEach(label => {
            scene.add(label);
        });
    }
    
    /**
     * 移除所有标签
     */
    public removeLabelsFromScene(scene: THREE.Scene): void {
        this.labels.forEach(label => {
            scene.remove(label);
        });
    }
    
    /**
     * 渲染标签
     */
    public render(scene: THREE.Scene, camera: THREE.Camera): void {
        this.labelRenderer.render(scene, camera);
    }
    
    /**
     * 窗口大小调整
     */
    private onResize = (): void => {
        this.labelRenderer.setSize(window.innerWidth, window.innerHeight);
    };
    
    /**
     * 设置标签可见性
     */
    public setLabelsVisible(visible: boolean): void {
        this.labels.forEach(label => {
            label.visible = visible;
        });
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        window.removeEventListener('resize', this.onResize);
        this.container.removeChild(this.labelRenderer.domElement);
        this.labels.clear();
    }
}
