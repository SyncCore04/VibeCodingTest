# SmartCart System 智能购物车系统

Java 面向对象练习项目：超市购物车结算控制台程序。

## 功能

- 添加普通商品 / 打折商品到购物车
- 按编号移除商品
- 查看购物车明细
- 结算：满 3 件及以上整单 9.5 折，否则原价

## 面向对象特性

- **封装**：属性私有，通过 getter/setter 和业务方法访问
- **继承**：`DiscountProduct extends Product`，`super()` 复用父类构造
- **多态**：`ArrayList<Product>` 混合存储，`getPrice()` 运行时自动分派

## 项目结构

```
Product.java          商品父类
DiscountProduct.java  打折商品子类（重写 getPrice）
ShoppingCart.java     购物车类（增删查 + 结算）
Main.java             控制台菜单入口
```

## 运行

```bash
javac -encoding UTF-8 *.java
java Main
```

或在 IDEA 中直接运行 `Main.main()`。
