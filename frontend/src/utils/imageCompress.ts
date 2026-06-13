/**
 * 图片压缩工具。
 *
 * 使用 Canvas 重采样，优先输出 WebP 格式以减小体积。
 * 异步执行，不阻塞主线程。
 */

export interface CompressOptions {
  /** 最大宽度（px），默认 1920 */
  maxWidth?: number
  /** 最大高度（px），默认 1080 */
  maxHeight?: number
  /** 压缩质量 0-1，默认 0.85 */
  quality?: number
  /** 输出格式，默认 webp（支持时） */
  format?: 'webp' | 'jpeg' | 'png'
}

const DEFAULTS: Required<CompressOptions> = {
  maxWidth: 1920,
  maxHeight: 1080,
  quality: 0.85,
  format: 'webp'
}

/**
 * 尝试判断浏览器是否支持 WebP 编码。
 */
function supportsWebP(): boolean {
  const canvas = document.createElement('canvas')
  canvas.width = 1
  canvas.height = 1
  return canvas.toDataURL('image/webp').indexOf('image/webp') === 5
}

/**
 * 压缩图片文件。
 * 如果原图尺寸小于阈值，则直接返回原文件（跳过压缩）。
 *
 * @param file 原图片文件
 * @param options 压缩选项
 * @returns 压缩后的 File 对象
 */
export function compressImage(file: File, options?: CompressOptions): Promise<File> {
  const opts = { ...DEFAULTS, ...options }

  // 格式降级：不支持 WebP 时回退到 JPEG
  if (opts.format === 'webp' && !supportsWebP()) {
    opts.format = 'jpeg'
  }

  return new Promise((resolve) => {
    // 小图直接跳过
    if (file.size < 100 * 1024) {
      resolve(file)
      return
    }

    const img = new Image()
    const url = URL.createObjectURL(file)

    img.onload = () => {
      URL.revokeObjectURL(url)

      let { width, height } = img

      // 等比例缩放
      if (width > opts.maxWidth) {
        height = Math.round((height * opts.maxWidth) / width)
        width = opts.maxWidth
      }
      if (height > opts.maxHeight) {
        width = Math.round((width * opts.maxHeight) / height)
        height = opts.maxHeight
      }

      // 不需要缩放则返回原文件
      if (width === img.naturalWidth && height === img.naturalHeight) {
        resolve(file)
        return
      }

      // Canvas 重采样
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      if (!ctx) {
        resolve(file)
        return
      }

      ctx.drawImage(img, 0, 0, width, height)

      const mimeType = opts.format === 'webp' ? 'image/webp' : `image/${opts.format}`
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            resolve(file)
            return
          }
          const suffix = opts.format === 'jpeg' ? 'jpg' : opts.format
          const name = file.name.replace(/\.[^.]+$/, `.${suffix}`)
          const compressed = new File([blob], name, {
            type: mimeType,
            lastModified: Date.now()
          })
          resolve(compressed)
        },
        mimeType,
        opts.quality
      )
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(file) // 加载失败就返回原文件
    }

    img.src = url
  })
}
