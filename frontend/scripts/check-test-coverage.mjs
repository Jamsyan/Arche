/**
 * 校验源文件与测试文件的对应关系。
 *
 * 规则：
 *   src/utils/foo.ts        ↔  src/tests/utils/foo.test.ts
 *   src/services/request.ts  ↔  src/tests/services/request.test.ts
 *
 * 用法：
 *   node scripts/check-test-coverage.mjs            # 列出缺失测试的文件
 *   node scripts/check-test-coverage.mjs --strict   # 缺失时 exit code 1
 *   node scripts/check-test-coverage.mjs --list     # 列出所有对应关系
 */

import { readdirSync, statSync, existsSync } from 'node:fs'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

let ROOT = fileURLToPath(new URL('..', import.meta.url))
let SRC = join(ROOT, 'src')
let TESTS = join(ROOT, 'src', 'tests')

// 如果脚本在子目录中（如 frontend/scripts/），src 目录不存在，需调整
if (!existsSync(SRC)) {
  ROOT = join(ROOT, '..')
  SRC = join(ROOT, 'src')
  TESTS = join(ROOT, 'src', 'tests')
}

// 不要求有测试的文件（入口、类型定义、自动生成）
const EXCLUDE_PATTERNS = [
  (f) => f.endsWith('.d.ts'),
  (f) => f === 'main.ts',
  (f) => f === 'env.d.ts',
  (f) => f === 'auto-imports.d.ts',
  (f) => f === 'components.d.ts',
]

// 测试目录相对于 ROOT 的路径，用于在 collectFiles 中跳过 tests 目录
const TEST_DIR = relative(ROOT, TESTS)

function isExcluded(relPath) {
  return EXCLUDE_PATTERNS.some((p) => p(relPath))
}

/** 遍历目录收集所有 .ts 文件 */
function collectFiles(dir, baseDir) {
  const result = []
  try {
    const entries = readdirSync(dir)
    for (const entry of entries) {
      const full = join(dir, entry)
      const rel = relative(baseDir, full)
      const stat = statSync(full)
      if (stat.isDirectory()) {
        // 跳过 node_modules、tests 目录自身
        if (entry === 'node_modules' || entry === '.git') continue
        if (rel.startsWith(TEST_DIR)) continue
        result.push(...collectFiles(full, baseDir))
      } else if (
        entry.endsWith('.ts') &&
        !entry.endsWith('.test.ts') &&
        !entry.endsWith('.spec.ts') &&
        !isExcluded(rel)
      ) {
        result.push(rel)
      }
    }
  } catch { /* ignore */ }
  return result
}

/** 根据源文件路径推导期望的测试文件路径 */
function expectedTestPath(srcRelPath) {
  // 统一转正斜杠再替换，避免 Windows 反斜杠问题
  const normalized = srcRelPath.replace(/\\/g, '/')
  const testPath = normalized.replace(/^src\//, 'src/tests/').replace(/\.ts$/, '.test.ts')
  return join(ROOT, testPath)
}

/** 检查测试文件是否存在 */
function testExists(expected) {
  return existsSync(expected)
}

// ── 主逻辑 ──
const strict = process.argv.includes('--strict')
const listMode = process.argv.includes('--list')

const sourceFiles = collectFiles(SRC, ROOT)
const missing = []
let totalSource = 0

for (const srcRel of sourceFiles) {
  totalSource++
  const expected = expectedTestPath(srcRel)
  if (!testExists(expected)) {
    missing.push({ src: srcRel, test: expected })
  } else if (listMode) {
    console.log(`✅  ${srcRel}  →  ${relative(ROOT, expected)}`)
  }
}

// 也在 tests 目录下找孤儿测试文件（没有对应源文件的）
const testFiles = collectFiles(TESTS, ROOT)
const orphans = []
for (const testRel of testFiles) {
  const expectedSource = testRel.replace(/\\/g, '/').replace(/src\/tests\//, 'src/').replace(/\.test\.ts$/, '.ts')
  if (!existsSync(join(ROOT, expectedSource))) {
    orphans.push(testRel)
  }
}

// ── 输出 ──
const coveredCount = totalSource - missing.length

if (missing.length > 0) {
  console.log(`\n⚠️  发现 ${missing.length} 个源文件缺少对应的测试文件:\n`)
  for (const { src, test } of missing) {
    console.log(`   📄 ${src}`)
    console.log(`   🧪 ${test}\n`)
  }
} else {
  console.log(`\n✅ 全部 ${totalSource} 个源文件都有对应的测试文件`)
}

if (orphans.length > 0) {
  console.log(`\n⚠️  发现 ${orphans.length} 个孤儿测试文件（无对应源文件）:\n`)
  for (const o of orphans) {
    console.log(`   🧪 ${o}`)
  }
}

console.log(`\n📊 源文件: ${totalSource}  测试文件: ${coveredCount}  缺失: ${missing.length}${orphans.length > 0 ? `  孤儿: ${orphans.length}` : ''}`)

if (strict && missing.length > 0) {
  process.exit(1)
}
