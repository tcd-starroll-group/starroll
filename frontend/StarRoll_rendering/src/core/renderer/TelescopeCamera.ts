import * as THREE from 'three';

/**
 * 望远镜相机控制器
 * 实现 StarWalk2 风格的缩放
 * - 改变 FOV（不是靠近物体）
 * - 相机固定在地面
 * - 星点大小锁定
 */
export class TelescopeCamera {
    private camera: THREE.PerspectiveCamera;
    private container: HTMLElement;
    
    // 缩放参数
    private zoom = 1.0;
    private readonly MIN_ZOOM = 0.5;
    private readonly MAX_ZOOM = 4.0;
    
    // FOV 范围
    private readonly DEFAULT_FOV = 75;
    private readonly MIN_FOV = 20;   // 最大放大
    private readonly MAX_FOV = 90;   // 最小放大
    
    // 地面约束
    private readonly OBSERVER_HEIGHT = 1.6;  // 人眼高度（米）
    
    // 相机方向
    private rotation = { azimuth: 0, altitude: 45 };  // 默认向北偏上
    
    // 回调
    private onZoomChange?: (zoom: number, fov: number) => void;
    
    constructor(camera: THREE.PerspectiveCamera, container: HTMLElement) {
        this.camera = camera;
        this.container = container;
        
        // 设置初始位置（地面观测者）
        this.camera.position.set(0, this.OBSERVER_HEIGHT, 0);
        
        // 设置初始朝向
        this.updateCameraDirection();
        
        // 设置控制
        this.setupControls();
    }
    
    /**
     * 设置控制
     */
    private setupControls(): void {
        let isDragging = false;
        let lastPosition = { x: 0, y: 0 };
        
        // 鼠标拖动
        this.container.addEventListener('mousedown', (e) => {
            isDragging = true;
            lastPosition = { x: e.clientX, y: e.clientY };
        });
        
        this.container.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - lastPosition.x;
            const deltaY = e.clientY - lastPosition.y;
            
            // 更新方位角和仰角
            this.rotation.azimuth += deltaX * 0.3;
            this.rotation.altitude -= deltaY * 0.3;
            
            // 限制仰角（不能看地下，不能翻过头顶）
            this.rotation.altitude = Math.max(-5, Math.min(90, this.rotation.altitude));
            
            // 归一化方位角
            this.rotation.azimuth = ((this.rotation.azimuth % 360) + 360) % 360;
            
            this.updateCameraDirection();
            lastPosition = { x: e.clientX, y: e.clientY };
        });
        
        this.container.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        // ⭐ 核心：滚轮缩放（改变 FOV）
        this.container.addEventListener('wheel', (e) => {
            e.preventDefault();
            
            const zoomSpeed = 0.002;
            this.zoom += e.deltaY * -zoomSpeed;
            this.zoom = Math.max(this.MIN_ZOOM, Math.min(this.MAX_ZOOM, this.zoom));
            
            this.applyZoom();
        }, { passive: false });
        
        // 触摸缩放
        let touchDistance = 0;
        this.container.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                touchDistance = Math.sqrt(dx * dx + dy * dy);
            }
        });
        
        this.container.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2 && touchDistance > 0) {
                e.preventDefault();
                
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const newDistance = Math.sqrt(dx * dx + dy * dy);
                
                const zoomDelta = (newDistance - touchDistance) * 0.005;
                this.zoom += zoomDelta;
                this.zoom = Math.max(this.MIN_ZOOM, Math.min(this.MAX_ZOOM, this.zoom));
                
                this.applyZoom();
                touchDistance = newDistance;
            }
        }, { passive: false });
    }
    
    /**
     * 应用缩放（改变 FOV）
     */
    private applyZoom(): void {
        // ⭐ 核心：通过 FOV 实现"望远镜"效果
        // zoom 1.0 → FOV 75
        // zoom 4.0 → FOV 20（强放大）
        const fov = this.DEFAULT_FOV / this.zoom;
        const clampedFOV = Math.max(this.MIN_FOV, Math.min(this.MAX_FOV, fov));
        
        this.camera.fov = clampedFOV;
        this.camera.updateProjectionMatrix();
        
        console.log(`🔭 缩放: ${this.zoom.toFixed(2)}x, FOV: ${clampedFOV.toFixed(1)}°`);
        
        // 触发回调（通知星场更新）
        if (this.onZoomChange) {
            this.onZoomChange(this.zoom, clampedFOV);
        }
    }
    
    /**
     * 更新相机朝向
     */
    private updateCameraDirection(): void {
        const azimuthRad = THREE.MathUtils.degToRad(this.rotation.azimuth);
        const altitudeRad = THREE.MathUtils.degToRad(this.rotation.altitude);
        
        // 计算朝向
        const direction = new THREE.Vector3(
            Math.sin(azimuthRad) * Math.cos(altitudeRad),
            Math.sin(altitudeRad),
            Math.cos(azimuthRad) * Math.cos(altitudeRad)
        );
        
        // 计算目标点
        const target = this.camera.position.clone().add(direction);
        this.camera.lookAt(target);
    }
    
    /**
     * 设置缩放变化回调
     */
    public setOnZoomChange(callback: (zoom: number, fov: number) => void): void {
        this.onZoomChange = callback;
    }
    
    /**
     * 从设备方向更新（AR 模式）
     */
    public updateFromDeviceSensor(azimuth: number, altitude: number): void {
        this.rotation.azimuth = azimuth;
        this.rotation.altitude = altitude;
        this.updateCameraDirection();
    }
    
    /**
     * 获取当前朝向
     */
    public getOrientation(): { azimuth: number, altitude: number } {
        return { ...this.rotation };
    }
    
    /**
     * 获取缩放级别
     */
    public getZoom(): number {
        return this.zoom;
    }
}
