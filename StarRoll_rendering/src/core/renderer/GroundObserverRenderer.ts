import * as THREE from 'three';
import type { StarMeta } from '../../types/star-meta';
import type { ConstellationModel } from '../data/constellation-models';
import { HorizonCoordinates, ObserverLocation, OBSERVER_LOCATIONS } from '../astronomy/HorizonCoordinates';
import { loadStarCatalog } from '../../types/star-catalog';
import { constellationModels, constellationLinesWithModels } from '../data/constellation-models';
import { ModelLoader } from '../utils/GLTFLoader';
import { GlassConstellationMaterial } from '../materials/ConstellationMaterials';
import { sensorManager, type SensorData, type CameraOrientation } from '../Tensors/sensor';
import { StarLabelManager } from './StarLabelManager';
import { getStarName, formatStarDisplayName } from '../data/star-names';

/**
 * Star click information
 */
export interface StarClickInfo {
    hip: number;
    name: string;
    englishName: string;
    constellation: string;
    magnitude: number;
    bvColor: number;
    distance?: number;
    rightAscension: number;
    declination: number;
    altitude: number;
    azimuth: number;
    screenX: number;
    screenY: number;
    originalName: string;
    description: string;
    url: string;
    raw?: any;
}

// Helper constants
const degToRad = Math.PI / 180;

/**
 * Ground Observer Renderer
 * Simulates sky view from Earth surface
 */
export class GroundObserverRenderer {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private container: HTMLElement;

    // Observer parameters
    private observerLocation: ObserverLocation = OBSERVER_LOCATIONS.SHANGHAI;
    private observationTime: Date = new Date();
    private localSiderealTime: number = 0;

    // Render objects
    private starPoints: THREE.Points | null = null;
    private ground: THREE.Mesh | null = null;
    private horizon: THREE.Line | null = null;
    private constellationModels: THREE.Group = new THREE.Group();
    private constellationLines: THREE.Group = new THREE.Group();

    // Star data
    private starMap: Map<number, { star: StarMeta, position: THREE.Vector3 }> = new Map();

    // Celestial sphere
    private readonly SKY_RADIUS = 1000;

    // Animation
    private animationFrameId: number | null = null;

    // AR mode
    private arMode: boolean = false;
    private cameraOrientation: CameraOrientation | null = null;

    // Smoothing
    private targetQuaternion = new THREE.Quaternion();
    private lastOrientation: number = 0;

    // AR temp variables
    private _euler = new THREE.Euler();
    private _q0 = new THREE.Quaternion();
    private _q1 = new THREE.Quaternion(-Math.sqrt(0.5), 0, 0, Math.sqrt(0.5));
    private _zee = new THREE.Vector3(0, 0, 1);

    // Camera
    private videoElement: HTMLVideoElement | null = null;
    private videoStream: MediaStream | null = null;

    // Manual control
    private manualRotation = { x: 0, y: 0 };
    private isDragging = false;
    private lastMousePosition = { x: 0, y: 0 };
    private zoom = 1.0;

    // Labels
    private labelManager: StarLabelManager;

    // Click detection
    private raycaster: THREE.Raycaster = new THREE.Raycaster();
    private mouse: THREE.Vector2 = new THREE.Vector2();
    private onStarClickCallback: ((starInfo: StarClickInfo) => void) | null = null;

    // Location
    private isRequestingLocation = false;
    private locationPermissionGranted = false;

    constructor(container: HTMLElement) {
        this.container = container;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000510);

        // FOV tuned for mobile camera matching
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            this.SKY_RADIUS * 2
        );

        this.camera.position.set(0, 0, 0);
        this.camera.lookAt(0, 1, 0);
        this.camera.up.set(0, 1, 0);

        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
        container.appendChild(this.renderer.domElement);

        this.createGround();
        this.createHorizon();
        this.setupLighting();

        this.labelManager = new StarLabelManager(container);
        this.loadStarField();
        this.animate();
        this.setupMouseControl();
        this.setupClickDetection();

        window.addEventListener('resize', this.onWindowResize);
        window.addEventListener('orientationchange', () => {
            setTimeout(this.onWindowResize, 200);
        });

        console.log('Ground Observer Renderer initialized');
    }

    /**
     * Create ground plane with fade-out grid
     */
    private createGround(): void {
        const geometry = new THREE.CircleGeometry(2000, 64);
        const material = new THREE.ShaderMaterial({
            uniforms: {
                uColor: { value: new THREE.Color(0x0a0a15) }
            },
            vertexShader: `
                varying vec2 vUv;
                varying vec3 vPosition;
                void main() {
                    vUv = uv;
                    vPosition = position;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 uColor;
                varying vec2 vUv;
                varying vec3 vPosition;
                void main() {
                    float dist = length(vPosition);
                    float fade = 1.0 - smoothstep(1000.0, 2000.0, dist);
                    float grid = 0.0;
                    float gridSize = 100.0;
                    if (mod(vPosition.x, gridSize) < 2.0 || mod(vPosition.y, gridSize) < 2.0) {
                        grid = 0.05;
                    }
                    vec3 color = uColor + vec3(grid);
                    gl_FragColor = vec4(color, fade);
                }
            `,
            transparent: true,
            side: THREE.DoubleSide
        });
        this.ground = new THREE.Mesh(geometry, material);
        this.ground.rotation.x = -Math.PI / 2;
        this.ground.position.y = 0;
        this.scene.add(this.ground);
    }

    /**
     * Create horizon circle line
     */
    private createHorizon(): void {
        const points: THREE.Vector3[] = [];
        const segments = 128;
        const horizonRadius = 1500;
        for (let i = 0; i <= segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            const x = Math.cos(angle) * horizonRadius;
            const z = Math.sin(angle) * horizonRadius;
            points.push(new THREE.Vector3(x, 0, z));
        }
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0x4488ff,
            transparent: true,
            opacity: 0.3
        });
        this.horizon = new THREE.Line(geometry, material);
        this.scene.add(this.horizon);
    }

    private setupLighting(): void {
        const ambientLight = new THREE.AmbientLight(0x202040, 0.2);
        this.scene.add(ambientLight);
    }

    private async loadStarField(): Promise<void> {
        try {
            console.log('Loading ground observer star field...');
            const stars = await loadStarCatalog();
            this.localSiderealTime = HorizonCoordinates.calculateLocalSiderealTime(
                this.observerLocation.longitude,
                this.observationTime
            );
            this.createStarFieldFromCatalog(stars);
            console.log('Ground observer star field loaded');
        } catch (error) {
            console.error('Failed to load star field:', error);
        }
    }

    private createStarFieldFromCatalog(stars: StarMeta[]): void {
        const brightStars: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[] = [];
        const mediumStars: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[] = [];
        const dimStars: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[] = [];

        stars.forEach(star => {
            if (star.magnitude > 4.5) return;

            const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.observerLocation.latitude,
                this.localSiderealTime
            );

            if (altitude < 0) return;

            const pos = HorizonCoordinates.horizonToVector3(altitude, azimuth, this.SKY_RADIUS);
            const color = this.bvToRGB(star.bvColor);
            this.starMap.set(star.hIP, { star, position: pos });

            const starData = { pos, color, star };
            if (star.magnitude < 1.0) brightStars.push(starData);
            else if (star.magnitude < 2.5) mediumStars.push(starData);
            else dimStars.push(starData);
        });

        if (this.starPoints) this.scene.remove(this.starPoints);

        const starGroup = new THREE.Group();
        starGroup.name = 'Stars';

        if (brightStars.length > 0)
            starGroup.add(this.createStarPoints(brightStars, '/texture/star16x16_ray.png', 8.0));
        if (mediumStars.length > 0)
            starGroup.add(this.createStarPoints(mediumStars, '/texture/star16x16.png', 5.0));
        if (dimStars.length > 0)
            starGroup.add(this.createStarPoints(dimStars, '/texture/star16x16.png', 3.0));

        this.starPoints = starGroup as any;
        this.scene.add(starGroup);
    }

    private createStarPoints(
        starsData: { pos: THREE.Vector3, color: THREE.Color, star: StarMeta }[],
        texturePath: string,
        baseSize: number
    ): THREE.Points {
        const positions: number[] = [];
        const colors: number[] = [];
        const magnitudes: number[] = [];
        const twinklePhases: number[] = [];

        starsData.forEach(({ pos, color, star }) => {
            positions.push(pos.x, pos.y, pos.z);
            colors.push(color.r, color.g, color.b);
            magnitudes.push(star.magnitude);
            twinklePhases.push(Math.random() * Math.PI * 2);
        });

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('magnitude', new THREE.Float32BufferAttribute(magnitudes, 1));
        geometry.setAttribute('twinklePhase', new THREE.Float32BufferAttribute(twinklePhases, 1));

        const isRayTexture = texturePath.includes('ray');
        const texture = this.createProceduralStarTexture(isRayTexture);
        const material = this.createTwinkleStarMaterial(texture, baseSize);

        return new THREE.Points(geometry, material);
    }

    private createTwinkleStarMaterial(texture: THREE.Texture, baseSize: number): THREE.ShaderMaterial {
        return new THREE.ShaderMaterial({
            uniforms: {
                uTexture: { value: texture },
                uSize: { value: baseSize },
                uTime: { value: 0 },
                uPixelRatio: { value: window.devicePixelRatio }
            },
            vertexShader: `
                attribute vec3 color;
                attribute float magnitude;
                attribute float twinklePhase;
                uniform float uSize;
                uniform float uTime;
                uniform float uPixelRatio;
                varying vec3 vColor;
                varying float vTwinkle;
                void main() {
                    vColor = color;
                    float twinkleSpeed = 1.0 + magnitude * 0.3;
                    float twinkleAmount = 0.15 + (6.0 - magnitude) * 0.05;
                    float twinkle = sin(uTime * twinkleSpeed + twinklePhase) * twinkleAmount;
                    vTwinkle = 1.0 + twinkle;
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    gl_PointSize = uSize * vTwinkle * uPixelRatio;
                }
            `,
            fragmentShader: `
                uniform sampler2D uTexture;
                varying vec3 vColor;
                varying float vTwinkle;
                void main() {
                    vec4 texColor = texture2D(uTexture, gl_PointCoord);
                    vec3 finalColor = texColor.rgb * vColor * vTwinkle;
                    float alpha = texColor.a;
                    gl_FragColor = vec4(finalColor, alpha);
                }
            `,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
    }

    private createProceduralStarTexture(withRays: boolean = false): THREE.CanvasTexture {
        const size = 128;
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d')!;
        ctx.clearRect(0, 0, size, size);
        const center = size / 2;

        if (withRays) {
            ctx.save();
            ctx.translate(center, center);
            const rayLength = size * 0.45;
            const rayWidth = 2;
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.lineWidth = rayWidth;
            ctx.lineCap = 'round';
            for (let i = 0; i < 4; i++) {
                ctx.rotate(Math.PI / 4);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(0, -rayLength);
                ctx.stroke();
                ctx.rotate(Math.PI / 4);
            }
            ctx.restore();
        }

        const gradient = ctx.createRadialGradient(center, center, 0, center, center, size / 2);
        gradient.addColorStop(0, 'rgba(255,255,255,1.0)');
        gradient.addColorStop(0.3, 'rgba(255,255,255,0.8)');
        gradient.addColorStop(0.8, 'rgba(255,255,255,0.1)');
        gradient.addColorStop(1.0, 'rgba(255,255,255,0.0)');

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, size, size);

        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    private bvToRGB(bv: number): THREE.Color {
        let r: number, g: number, b: number;
        if (bv < 0) { r = 0.7; g = 0.8; b = 1.0; }
        else if (bv < 0.5) { const t = bv / 0.5; r = 0.8 + t * 0.2; g = 0.9 + t * 0.1; b = 1.0 - t * 0.1; }
        else if (bv < 1.0) { const t = (bv - 0.5) / 0.5; r = 1.0; g = 1.0 - t * 0.15; b = 0.9 - t * 0.25; }
        else if (bv < 1.5) { const t = (bv - 1.0) / 0.5; r = 1.0; g = 0.85 - t * 0.2; b = 0.65 - t * 0.25; }
        else { r = 1.0; g = 0.65; b = 0.4; }
        return new THREE.Color(r, g, b);
    }

    private setupMouseControl(): void {
        this.renderer.domElement.addEventListener('mousedown', (e) => {
            if (this.arMode) return;
            this.isDragging = true;
            this.lastMousePosition = { x: e.clientX, y: e.clientY };
        });

        this.renderer.domElement.addEventListener('mousemove', (e) => {
            if (!this.isDragging || this.arMode) return;
            const deltaX = e.clientX - this.lastMousePosition.x;
            const deltaY = e.clientY - this.lastMousePosition.y;
            this.manualRotation.y += deltaX * 0.005;
            this.manualRotation.x -= deltaY * 0.005;
            this.manualRotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.manualRotation.x));
            this.lastMousePosition = { x: e.clientX, y: e.clientY };
            this.updateCameraFromManual();
        });

        this.renderer.domElement.addEventListener('mouseup', () => { this.isDragging = false; });
        this.renderer.domElement.addEventListener('mouseleave', () => { this.isDragging = false; });

        const handleZoom = (delta: number) => {
            this.zoom += delta;
            this.zoom = Math.max(0.5, Math.min(3.0, this.zoom));
            this.camera.fov = 60 / this.zoom;
            this.camera.updateProjectionMatrix();
            if (this.starPoints && this.starPoints.material instanceof THREE.ShaderMaterial) {
                this.starPoints.material.uniforms.uBaseSize.value = 120.0 * this.zoom;
            }
        };

        this.renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            handleZoom(e.deltaY * -0.001);
        }, { passive: false });

        let touchDistance = 0;
        this.renderer.domElement.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                touchDistance = Math.sqrt(dx * dx + dy * dy);
            }
        });

        this.renderer.domElement.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2 && touchDistance > 0) {
                e.preventDefault();
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const newDistance = Math.sqrt(dx * dx + dy * dy);
                handleZoom((newDistance - touchDistance) * 0.01);
                touchDistance = newDistance;
            }
        }, { passive: false });
    }

    public async enableARMode(): Promise<boolean> {
        console.log('Enabling AR mode...');
        if (typeof DeviceOrientationEvent === 'undefined') {
            console.error('Device orientation not supported');
            return false;
        }

        const permission = await sensorManager.requestPermission();
        if (permission === 'denied') {
            console.error('Sensor permission denied');
            return false;
        }

        sensorManager.addListener(this.handleSensorData);
        sensorManager.startListening();

        this.arMode = true;
        this.scene.background = null;
        if (this.ground) this.ground.visible = false;
        if (this.horizon) this.horizon.visible = false;

        await this.startCamera();
        console.log('AR mode enabled');
        return true;
    }

    public disableARMode(): void {
        if (!this.arMode) return;

        sensorManager.removeListener(this.handleSensorData);
        sensorManager.stopListening();

        this.arMode = false;
        this.stopCamera();

        this.scene.background = new THREE.Color(0x000510);
        if (this.ground) this.ground.visible = true;
        if (this.horizon) this.horizon.visible = true;

        this.camera.quaternion.set(0, 0, 0, 1);
        this.camera.lookAt(0, 1, 0);
        this.camera.up.set(0, 1, 0);

        console.log('AR mode disabled');
    }

    private handleSensorData = (data: SensorData): void => {
        if (!this.arMode) return;
        this.updateCameraFromSensor();
    };

    private updateCameraFromSensor(): void {
        const lastData = sensorManager.getLastData();
        if (!lastData || lastData.alpha === null || lastData.beta === null || lastData.gamma === null) return;

        let alpha = 0;
        if (typeof lastData.webkitCompassHeading === 'number') {
            alpha = (360 - lastData.webkitCompassHeading) * degToRad;
        } else {
            alpha = lastData.alpha * degToRad;
        }

        const beta = lastData.beta * degToRad;
        const gamma = lastData.gamma * degToRad;
        const orient = lastData.screenOrientation * degToRad;

        this._euler.set(beta, alpha, -gamma, 'YXZ');
        this.targetQuaternion.setFromEuler(this._euler);
        this.targetQuaternion.multiply(this._q1);
        this._q0.setFromAxisAngle(this._zee, -orient);
        this.targetQuaternion.multiply(this._q0);

        if (this.lastOrientation !== lastData.screenOrientation) {
            this.camera.quaternion.copy(this.targetQuaternion);
            this.lastOrientation = lastData.screenOrientation;
        }
    }

    private updateCameraFromManual(): void {
        const euler = new THREE.Euler(
            this.manualRotation.x,
            this.manualRotation.y,
            0,
            'YXZ'
        );
        this.camera.rotation.copy(euler);
    }

    /**
     * Main render loop with adaptive AR smoothing
     */
    private animate = () => {
        const time = Date.now() * 0.001;

        if (this.arMode) {
            const angleDiff = this.camera.quaternion.angleTo(this.targetQuaternion);
            let slerpFactor = 0.1;

            if (angleDiff > 0.3) {
                slerpFactor = 0.8;
            } else if (angleDiff > 0.05) {
                slerpFactor = 0.3;
            } else if (angleDiff < 0.002) {
                slerpFactor = 0.02;
            } else {
                slerpFactor = 0.1;
            }

            this.camera.quaternion.slerp(this.targetQuaternion, slerpFactor);
        }

        if (this.starPoints) {
            this.starPoints.traverse((child: any) => {
                if (child instanceof THREE.Points && child.material instanceof THREE.ShaderMaterial) {
                    child.material.uniforms.uTime.value = time;
                }
            });
        }

        this.renderer.render(this.scene, this.camera);
        this.labelManager.render(this.scene, this.camera);
        this.animationFrameId = requestAnimationFrame(this.animate);
    };

    public setObserverLocation(location: ObserverLocation): void {
        this.observerLocation = location;
        this.loadStarField();
    }

    public setObservationTime(time: Date): void {
        this.observationTime = time;
        this.loadStarField();
    }

    public getStats() {
        return {
            visibleStars: this.starPoints?.geometry.attributes.position.count || 0,
            visibleConstellations: this.constellationModels.children.length,
            observerLocation: this.observerLocation.name,
            localSiderealTime: this.localSiderealTime.toFixed(2),
            arMode: this.arMode,
            sensorPermission: sensorManager.getPermissionState()
        };
    }

    public getCameraOrientation(): { azimuth: number, altitude: number } {
        const direction = new THREE.Vector3(0, 0, -1);
        direction.applyQuaternion(this.camera.quaternion);

        let azimuth = Math.atan2(direction.x, -direction.z) * 180 / Math.PI;
        let altitude = Math.asin(direction.y) * 180 / Math.PI;

        return {
            azimuth: ((azimuth % 360) + 360) % 360,
            altitude: altitude
        };
    }

    public isARMode(): boolean { return this.arMode; }

    private onWindowResize = () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    };

    public dispose(): void {
        if (this.animationFrameId) cancelAnimationFrame(this.animationFrameId);
        if (this.arMode) this.disableARMode();
        window.removeEventListener('resize', this.onWindowResize);

        if (this.starPoints) {
            this.starPoints.geometry.dispose();
            if (this.starPoints.material instanceof THREE.Material)
                this.starPoints.material.dispose();
        }

        this.labelManager.dispose();
        this.renderer.dispose();
        this.container.removeChild(this.renderer.domElement);
    }

    public setConstellationLinesVisible(visible: boolean): void { this.constellationLines.visible = visible; }
    public setStarLabelsVisible(visible: boolean): void { this.labelManager.setLabelsVisible(visible); }
    public setOnStarClick(callback: (starInfo: StarClickInfo) => void): void { this.onStarClickCallback = callback; }

    private setupClickDetection(): void {
        this.raycaster.params.Points = { threshold: 50.0 };
        const handleClick = (clientX: number, clientY: number) => {
            this.mouse.x = (clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(clientY / window.innerHeight) * 2 + 1;
            this.raycaster.setFromCamera(this.mouse, this.camera);
            if (this.starPoints) {
                const intersects = this.raycaster.intersectObject(this.starPoints);
                if (intersects.length > 0 && intersects[0].index !== undefined) {
                    this.handleStarClick(intersects[0].index);
                }
            }
        };

        this.renderer.domElement.addEventListener('click', (e) => {
            if (!this.isDragging) handleClick(e.clientX, e.clientY);
        });
        this.renderer.domElement.addEventListener('touchend', (e) => {
            if (e.changedTouches.length > 0)
                handleClick(e.changedTouches[0].clientX, e.changedTouches[0].clientY);
        });
    }

    private async handleStarClick(index: number): Promise<void> {
        let starData;
        let i = 0;
        for (const data of this.starMap.values()) {
            if (i === index) { starData = data; break; }
            i++;
        }

        if (starData && this.onStarClickCallback) {
            const { star, position } = starData;
            const nameData = getStarName(star.hIP);

            const { altitude, azimuth } = HorizonCoordinates.equatorialToHorizon(
                star.equatorialCoordinate.rightAscension,
                star.equatorialCoordinate.declination,
                this.observerLocation.latitude,
                this.localSiderealTime
            );

            const screenPos = position.clone();
            screenPos.project(this.camera);
            const screenX = (screenPos.x * 0.5 + 0.5) * window.innerWidth;
            const screenY = (-(screenPos.y * 0.5) + 0.5) * window.innerHeight;

            let detailedData: any = {};
            let fetchSuccess = false;

            const baseUrl = import.meta.env?.BASE_URL || '/';
            const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

            const pathsToTry = [
                `${cleanBase}/data/star-catalog/stars_data/HIP_${star.hIP}.json`
            ];

            for (const fetchUrl of pathsToTry) {
                try {
                    const response = await fetch(fetchUrl);
                    const contentType = response.headers.get("content-type");
                    if (response.ok && contentType && contentType.indexOf("application/json") !== -1) {
                        detailedData = await response.json();
                        fetchSuccess = true;
                        break;
                    }
                } catch (error) {
                    console.warn(`Path failed: ${fetchUrl}`, error);
                }
            }

            if (!fetchSuccess) {
                alert(`HIP_${star.hIP}.json not found. Check public folder.`);
            }

            this.onStarClickCallback({
                hip: star.hIP,
                name: nameData?.chinese || `HIP ${star.hIP}`,
                englishName: nameData?.english || '',
                constellation: nameData?.constellation || 'Unknown',
                magnitude: star.magnitude,
                bvColor: star.bvColor,
                distance: star.distance,
                rightAscension: star.equatorialCoordinate.rightAscension,
                declination: star.equatorialCoordinate.declination,
                altitude,
                azimuth,
                screenX,
                screenY,
                originalName: detailedData.name || '',
                description: detailedData.description || '',
                url: detailedData.url || '',
                raw: detailedData
            });
        }
    }

    public async requestUserLocation(): Promise<ObserverLocation | null> {
        if (this.isRequestingLocation) return null;
        if (!('geolocation' in navigator)) return null;

        this.isRequestingLocation = true;
        try {
            const position = await new Promise<GeolocationPosition>((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
            });

            const { latitude, longitude } = position.coords;
            this.locationPermissionGranted = true;
            const userLocation = { name: 'Current Location', latitude, longitude };
            this.setObserverLocation(userLocation);
            return userLocation;
        } catch (error) {
            return null;
        } finally {
            this.isRequestingLocation = false;
        }
    }

    public getLocationPermissionState(): 'granted' | 'prompt' | 'denied' {
        return this.locationPermissionGranted ? 'granted' : 'prompt';
    }

    public async useCurrentLocationAndTime(): Promise<boolean> {
        this.setObservationTime(new Date());
        return (await this.requestUserLocation()) !== null;
    }

    private async startCamera(): Promise<void> {
        try {
            if (!this.videoElement) {
                this.videoElement = document.createElement('video');
                this.videoElement.setAttribute('playsinline', '');
                this.videoElement.setAttribute('webkit-playsinline', '');
                Object.assign(this.videoElement.style, {
                    position: 'fixed',
                    top: '0',
                    left: '0',
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    zIndex: '-1',
                    pointerEvents: 'none'
                });
                this.container.appendChild(this.videoElement);
            }

            const constraints = {
                video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
                audio: false
            };
            this.videoStream = await navigator.mediaDevices.getUserMedia(constraints);
            this.videoElement.srcObject = this.videoStream;
            await this.videoElement.play();
        } catch (error) {
            console.error('Camera failed', error);
            throw error;
        }
    }

    private stopCamera(): void {
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
            this.videoStream = null;
        }
        if (this.videoElement) {
            this.videoElement.srcObject = null;
            this.videoElement.remove();
            this.videoElement = null;
        }
    }
}