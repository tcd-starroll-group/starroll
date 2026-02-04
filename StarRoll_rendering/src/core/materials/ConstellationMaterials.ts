import * as THREE from 'three';

/**
 * 玻璃感星座材质 Shader
 * 特点：半透明 + 强边缘光 (Rim Light) + 内部菲涅尔
 */
export const GlassConstellationMaterial = new THREE.ShaderMaterial({
    uniforms: {
        uColor: { value: new THREE.Color(0x88ccff) }, // 淡蓝紫色
        uRimColor: { value: new THREE.Color(0xffffff) }, // 白色边缘
        uRimPower: { value: 2.0 }, // 边缘光锐度
        uOpacity: { value: 0.4 }, // 基础透明度
        uTime: { value: 0 }
    },
    transparent: true,
    side: THREE.DoubleSide, // 双面渲染以获得体积感
    depthWrite: false, // 不写入深度，避免遮挡内部线条
    blending: THREE.AdditiveBlending, // 叠加混合，更有光感
    
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
            
            // 混合颜色：中心淡，边缘亮
            vec3 finalColor = mix(uColor * 0.5, uRimColor, rimIntensity);
            
            // 呼吸效果
            float breath = 0.8 + 0.2 * sin(uTime * 1.5);
            
            gl_FragColor = vec4(finalColor, (uOpacity * 0.3 + rimIntensity * 0.7) * breath);
        }
    `
});

/**
 * 星座连线材质 (发光线条)
 */
export const ConstellationLineMaterial = new THREE.LineBasicMaterial({
    color: 0x4488ff,
    transparent: true,
    opacity: 0.4,
    linewidth: 1, // WebGL 限制，大部分浏览器只有 1
    depthWrite: false
});

