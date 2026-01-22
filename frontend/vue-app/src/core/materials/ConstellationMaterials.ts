import * as THREE from 'three';

/**
 * 玻璃感星座材质 Shader
 * 特点：半透明 + 强边缘光 (Rim Light) + 内部菲涅尔
 */
export const GlassConstellationMaterial = new THREE.ShaderMaterial({
    uniforms: {
        uColor: { value: new THREE.Color(0xaaccff) }, // 淡蓝白色
        uRimColor: { value: new THREE.Color(0xffffff) }, // 白色边缘
        uRimPower: { value: 1.8 }, // 边缘光锐度（降低以获得更宽的轮廓）
        uOpacity: { value: 0.6 }, // 增加基础透明度
        uTime: { value: 0 }
    },
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    
    vertexShader: `
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        
        void main() {
            vNormal = normalize(normalMatrix * normal);
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
            vViewPosition = -mvPosition.xyz;
            gl_Position = projectionMatrix * mvPosition;
        }
    `,
    fragmentShader: `
        uniform vec3 uColor;
        uniform vec3 uRimColor;
        uniform float uRimPower;
        uniform float uOpacity;
        uniform float uTime;
        
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        
        void main() {
            vec3 normal = normalize(vNormal);
            vec3 viewDir = normalize(vViewPosition);
            
            // 菲涅尔效应 (Fresnel)
            // dot(view, normal) 在中心是 1，边缘是 0
            float vdn = dot(viewDir, normal);
            float rim = 1.0 - abs(vdn); // abs 确保背面也有光
            
            // 增强边缘光
            float rimIntensity = pow(rim, uRimPower);
            
            // 混合颜色：创造清晰的白色轮廓效果
            vec3 finalColor = mix(uColor * 0.4, uRimColor, rimIntensity * 1.2);
            
            // 轻微呼吸效果
            float breath = 0.9 + 0.1 * sin(uTime * 1.5);
            
            // 增强整体可见度
            float alpha = (uOpacity * 0.4 + rimIntensity * 0.8) * breath;
            
            gl_FragColor = vec4(finalColor, alpha);
        }
    `
});

/**
 * 星座连线材质 (发光线条)
 */
export const ConstellationLineMaterial = new THREE.LineBasicMaterial({
    color: 0x88bbff,  // 更亮的蓝白色
    transparent: true,
    opacity: 0.6,     // 增加透明度让线条更明显
    linewidth: 1,
    depthWrite: false
});

