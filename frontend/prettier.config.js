/** @type {import('prettier').Config} */
export default {
  printWidth: 100, // 一行最多100字符
  tabWidth: 2, // 缩进2空格
  useTabs: false, // 不使用tab，用空格
  semi: false, // 不使用分号
  singleQuote: true, // 使用单引号
  quoteProps: 'as-needed', // 对象属性仅在需要时加引号
  jsxSingleQuote: false, // jsx使用双引号
  trailingComma: 'none', // 末尾不加逗号
  bracketSpacing: true, // 对象大括号两边加空格 { foo: bar }
  bracketSameLine: false, // html标签闭合 > 单独一行
  arrowParens: 'always', // 箭头函数参数总是加括号 (x) => x
  vueIndentScriptAndStyle: false, // vue文件中script和style标签不缩进
  endOfLine: 'lf' // 统一使用lf换行
}
