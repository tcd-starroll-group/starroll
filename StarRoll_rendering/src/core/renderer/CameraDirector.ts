import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

/**
 * 相机导演类
 * 负责：
 * 1. 基础的用户交互 (OrbitControls)
 * 2. 智能运镜 (聚焦目标、平滑过渡)
 * 3. 动态跟随 (锁定移动中的行星)
 */
export class CameraDirector {
    private camera: THREE.PerspectiveCamera;
    private controls: OrbitControls;
    
    // 聚焦状态
    private targetObject: THREE.Object3D | null = null;
    private targetPosition: THREE.Vector3 | null = null; // 用于固定点聚焦 (如星座中心)
    
    private isTransitioning: boolean = false;
    
    // 动画参数
    private transitionDuration: number = 1.5; // 秒
    private transitionTimer: number = 0;
    
    // 过渡起始/结束状态
    private startPos = new THREE.Vector3();
    private startTarget = new THREE.Vector3();
    private endPosOffset = new THREE.Vector3(); // 目标相对物体的偏移量
    
    // 默认视角 (查看整个太阳系)
    private defaultPosition = new THREE.Vector3(0, 300, 500);
    private defaultTarget = new THREE.Vector3(0, 0, 0);

    constructor(camera: THREE.PerspectiveCamera, domElement: HTMLElement) {
        this.camera = camera;
        this.controls = new OrbitControls(camera, domElement);
        
        // 优化 Controls 手感
        this.controls.enableDamping = true; // 阻尼惯性
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 10;
        this.controls.maxDistance = 2000;

        // 【新增】监听用户交互，打断自动运镜，进入自由浏览模式
        this.controls.addEventListener('start', () => {
            if (this.isTransitioning || this.targetObject || this.targetPosition) {
                // 如果正在自动运镜或锁定跟随，用户一动鼠标，立刻解锁
                this.stopFocus();
            }
        });
    }

    private stopFocus() {
        this.targetObject = null;
        this.targetPosition = null;
        this.isTransitioning = false;
    }

    /**
     * 聚焦到某个 3D 对象 (例如行星 Mesh)
     * @param object 目标对象
     * @param offsetDistance 摄像机距离目标的距离 (默认基于包围盒计算)
     */
    public focus(object: THREE.Object3D | null, offsetDistance: number = 0) {
        if (!object) {
            this.resetView();
            return;
        }

        this.targetObject = object;
        this.targetPosition = null; // 清除固定点目标
        this.startTransition(object.position, offsetDistance, object);
    }

    /**
     * 【新增】聚焦到空间中的某个固定点 (例如星座中心)
     */
    public focusPosition(position: THREE.Vector3, offsetDistance: number = 100) {
        this.targetObject = null;
        this.targetPosition = position.clone();
        this.startTransition(position, offsetDistance);
    }

    private startTransition(targetCenter: THREE.Vector3, offsetDistance: number, refObject?: THREE.Object3D) {
        this.isTransitioning = true;
        this.transitionTimer = 0;

        // 记录起点
        this.startPos.copy(this.camera.position);
        this.startTarget.copy(this.controls.target);

        // 计算理想的终点偏移
        let dist = offsetDistance;
        if (dist === 0 && refObject) {
             const geo = (refObject as THREE.Mesh).geometry;
             if (geo instanceof THREE.SphereGeometry) {
                 dist = geo.parameters.radius * 4.0; 
             } else {
                 dist = 50; 
             }
        }
        
        const relativeDir = new THREE.Vector3().subVectors(this.camera.position, targetCenter).normalize();
        if (relativeDir.lengthSq() < 0.001) relativeDir.set(0, 1, 1).normalize(); 
        
        this.endPosOffset.copy(relativeDir).multiplyScalar(dist);
    }

    /**
     * 重置回全局视角
     */
    public resetView() {
        this.targetObject = null;
        this.targetPosition = null;
        this.isTransitioning = true;
        this.transitionTimer = 0;

        this.startPos.copy(this.camera.position);
        this.startTarget.copy(this.controls.target);
        
        // 终点是绝对坐标
        this.endPosOffset.copy(this.defaultPosition);
    }

    /**
     * 每一帧更新
     */
    public update(deltaTime: number) {
        if (this.isTransitioning) {
            this.updateTransition(deltaTime);
        } else if (this.targetObject) {
            // 锁定跟随模式：相机一直看着物体
            this.controls.target.copy(this.targetObject.position);
        } else if (this.targetPosition) {
            // 锁定固定点模式
            this.controls.target.copy(this.targetPosition);
        }

        this.controls.update();
    }

    private updateTransition(dt: number) {
        this.transitionTimer += dt;
        const t = Math.min(this.transitionTimer / this.transitionDuration, 1.0);
        
        const ease = 1 - Math.pow(1 - t, 3); // Cubic Out

        // 1. 计算当前目标中心
        let targetCenter = this.defaultTarget;
        if (this.targetObject) targetCenter = this.targetObject.position;
        else if (this.targetPosition) targetCenter = this.targetPosition;

        // 2. 插值 Controls.target (观察点)
        this.controls.target.lerpVectors(this.startTarget, targetCenter, ease);

        // 3. 插值 Camera.position
        const endPos = new THREE.Vector3();
        if (this.targetObject || this.targetPosition) {
            endPos.addVectors(targetCenter, this.endPosOffset);
        } else {
            endPos.copy(this.endPosOffset); // Reset mode: endPosOffset is absolute
        }
        
        this.camera.position.lerpVectors(this.startPos, endPos, ease);

        if (t >= 1.0) {
            this.isTransitioning = false;
        }
    }
}
