import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

/**
 * 后处理管理器
 * HDR Pipeline + ACES Tone Mapping + Selective Bloom
 */
export class PostProcessingManager {
    private composer: EffectComposer;
    private bloomPass: UnrealBloomPass;
    private toneMappingPass: ShaderPass;
    
    // 曝光控制
    private exposure = 1.0;
    private targetExposure = 1.0;
    
    constructor(
        renderer: THREE.WebGLRenderer,
        scene: THREE.Scene,
        camera: THREE.Camera
    ) {
        // 启用 HDR
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        
        // 创建后处理链
        this.composer = new EffectComposer(renderer);
        
        // 1. 基础渲染 Pass
        const renderPass = new RenderPass(scene, camera);
        this.composer.addPass(renderPass);
        
        // 2. 选择性 Bloom（只对亮星/太阳/高亮边缘）
        this.bloomPass = new UnrealBloomPass(
            new THREE.Vector2(window.innerWidth, window.innerHeight),
            0.5,   // 强度（较低，避免整个屏幕糊掉）
            0.4,   // 半径
            0.85   // 阈值（高阈值，只有亮的东西才 bloom）
        );
        this.composer.addPass(this.bloomPass);
        
        // 3. ACES Tone Mapping Pass（自定义，更细腻）
        this.toneMappingPass = new ShaderPass(this.createACESShader());
        this.composer.addPass(this.toneMappingPass);
        
        console.log('🎨 后处理系统初始化完成');
        console.log('   - HDR Pipeline: ✅');
        console.log('   - ACES Tone Mapping: ✅');
        console.log('   - Selective Bloom: ✅');
    }
    
    /**
     * 创建 ACES Tone Mapping Shader
     */
    private createACESShader(): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                tDiffuse: { value: null },
                uExposure: { value: 1.0 }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform sampler2D tDiffuse;
                uniform float uExposure;
                varying vec2 vUv;
                
                // ACES Filmic Tone Mapping
                vec3 ACESFilm(vec3 x) {
                    float a = 2.51;
                    float b = 0.03;
                    float c = 2.43;
                    float d = 0.59;
                    float e = 0.14;
                    return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
                }
                
                void main() {
                    vec4 texel = texture2D(tDiffuse, vUv);
                    
                    // 应用曝光
                    vec3 color = texel.rgb * uExposure;
                    
                    // ACES tone mapping
                    color = ACESFilm(color);
                    
                    // 伽马校正
                    color = pow(color, vec3(1.0 / 2.2));
                    
                    gl_FragColor = vec4(color, texel.a);
                }
            `
        });
    }
    
    /**
     * 设置 Bloom 参数
     */
    public setBloomParams(strength: number, radius: number, threshold: number): void {
        this.bloomPass.strength = strength;
        this.bloomPass.radius = radius;
        this.bloomPass.threshold = threshold;
    }
    
    /**
     * 设置目标曝光（平滑过渡）
     */
    public setExposure(exposure: number, immediate: boolean = false): void {
        this.targetExposure = exposure;
        if (immediate) {
            this.exposure = exposure;
            this.toneMappingPass.uniforms.uExposure.value = exposure;
        }
    }
    
    /**
     * 更新（平滑曝光过渡）
     */
    public update(deltaTime: number): void {
        // 曝光平滑过渡
        if (Math.abs(this.exposure - this.targetExposure) > 0.01) {
            this.exposure += (this.targetExposure - this.exposure) * deltaTime * 2.0;
            this.toneMappingPass.uniforms.uExposure.value = this.exposure;
        }
    }
    
    /**
     * 渲染
     */
    public render(): void {
        this.composer.render();
    }
    
    /**
     * 窗口大小调整
     */
    public resize(width: number, height: number): void {
        this.composer.setSize(width, height);
    }
    
    /**
     * 清理
     */
    public dispose(): void {
        this.composer.passes.forEach(pass => {
            if (pass instanceof ShaderPass && pass.material) {
                pass.material.dispose();
            }
        });
    }
}
