// Vitest 全局 setup 文件
// 在所有测试文件运行之前执行，提供全局 mock 和辅助函数
/// <reference lib="dom" />
/* global FrameRequestCallback, CanvasLineCap, CanvasLineJoin, CanvasTextAlign, CanvasTextBaseline, GlobalCompositeOperation, CanvasDirection, ImageSmoothingQuality */
import { vi } from 'vitest'

// ════════════════════════════════════════════
// 1. requestAnimationFrame / cancelAnimationFrame mock
//    jsdom 不实现 rAF，需要手动 mock
// ════════════════════════════════════════════
let rafId = 0
const rafCallbacks = new Map<number, FrameRequestCallback>()

window.requestAnimationFrame = vi.fn((cb: FrameRequestCallback) => {
  rafId++
  rafCallbacks.set(rafId, cb)
  return rafId
})

window.cancelAnimationFrame = vi.fn((id: number) => {
  rafCallbacks.delete(id)
})

/**
 * 手动推进一帧动画，触发当前所有排队的 rAF 回调。
 * 在测试 spring.ts 等涉及动画的模块时使用。
 *
 * @param timestamp - 可选的时间戳，默认 performance.now()
 */
function advanceAnimationFrame(timestamp: number = performance.now()) {
  const ids = [...rafCallbacks.keys()]
  for (const id of ids) {
    const cb = rafCallbacks.get(id)
    if (cb) {
      rafCallbacks.delete(id)
      cb(timestamp)
    }
  }
}

/**
 * 清空所有待执行的 rAF 回调。
 */
function clearAnimationFrames() {
  rafCallbacks.clear()
}

// ════════════════════════════════════════════
// 2. Canvas 2D Context mock
//    jsdom 的 canvas.getContext('2d') 返回 null，
//    为测试 generateTextCover.ts 等 canvas 模块而 mock
// ════════════════════════════════════════════
function createMockCanvasContext(): CanvasRenderingContext2D {
  const ctx = {
    // 属性
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 1,
    lineCap: 'butt' as CanvasLineCap,
    lineJoin: 'miter' as CanvasLineJoin,
    font: '',
    textAlign: 'left' as CanvasTextAlign,
    textBaseline: 'alphabetic' as CanvasTextBaseline,
    filter: 'none',
    globalAlpha: 1,
    globalCompositeOperation: 'source-over' as GlobalCompositeOperation,
    shadowBlur: 0,
    shadowColor: '',
    shadowOffsetX: 0,
    shadowOffsetY: 0,
    miterLimit: 10,
    direction: 'ltr' as CanvasDirection,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'low' as ImageSmoothingQuality,

    // 方法
    fillRect: vi.fn(),
    clearRect: vi.fn(),
    strokeRect: vi.fn(),
    fillText: vi.fn(),
    strokeText: vi.fn(),
    measureText: vi.fn(() => ({
      width: 50,
      actualBoundingBoxAscent: 0,
      actualBoundingBoxDescent: 0,
      actualBoundingBoxLeft: 0,
      actualBoundingBoxRight: 0,
      fontBoundingBoxAscent: 0,
      fontBoundingBoxDescent: 0
    })),
    beginPath: vi.fn(),
    closePath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    bezierCurveTo: vi.fn(),
    quadraticCurveTo: vi.fn(),
    arc: vi.fn(),
    arcTo: vi.fn(),
    ellipse: vi.fn(),
    rect: vi.fn(),
    roundRect: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
    clip: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    scale: vi.fn(),
    rotate: vi.fn(),
    translate: vi.fn(),
    transform: vi.fn(),
    setTransform: vi.fn(),
    resetTransform: vi.fn(),
    drawImage: vi.fn(),
    createLinearGradient: vi.fn(() => ({
      addColorStop: vi.fn()
    })),
    createRadialGradient: vi.fn(() => ({
      addColorStop: vi.fn()
    })),
    createPattern: vi.fn(() => null),
    getImageData: vi.fn(() => ({ data: new Uint8ClampedArray(0), width: 0, height: 0 })),
    putImageData: vi.fn(),
    createImageData: vi.fn(() => ({ data: new Uint8ClampedArray(0), width: 0, height: 0 })),
    setLineDash: vi.fn(),
    getLineDash: vi.fn(() => []),
    isPointInPath: vi.fn(() => false),
    isPointInStroke: vi.fn(() => false),
    canvas: document.createElement('canvas'),
    getContextAttributes: vi.fn(() => null),
    reset: vi.fn()
  } as unknown as CanvasRenderingContext2D
  return ctx
}

// 只在 getContext 返回 null 时才 mock
const originalGetContext = HTMLCanvasElement.prototype.getContext
HTMLCanvasElement.prototype.getContext = vi.fn(function (
  this: HTMLCanvasElement,
  contextId: string,
  options?: any
) {
  if (contextId === '2d') {
    return createMockCanvasContext()
  }
  return originalGetContext.call(this, contextId as any, options)
})

// toDataURL 也需要 mock
HTMLCanvasElement.prototype.toDataURL = vi.fn(() => 'data:image/jpeg;base64,mocked')

// ════════════════════════════════════════════
// 3. Performance.now() 稳定化
//    避免测试因时间精度问题产生不稳定结果
// ════════════════════════════════════════════
let fakeNow = 1000
vi.spyOn(performance, 'now').mockImplementation(() => {
  fakeNow += 16 // ~60fps 的帧间隔
  return fakeNow
})

// ════════════════════════════════════════════
// 导出供测试使用
// ════════════════════════════════════════════
export { advanceAnimationFrame, clearAnimationFrames }
