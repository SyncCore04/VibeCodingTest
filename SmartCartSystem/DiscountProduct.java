/**
 * 打折商品子类
 * 【继承】使用 extends 关键字继承 Product，自动获得 id/name/price 属性及 getter/setter
 * 【多态】重写父类的 getPrice()，使同一方法调用产生不同行为
 */
public class DiscountProduct extends Product {

    // 【封装】子类新增私有属性：折扣力度（0.8 表示打8折）
    private double discount;

    /**
     * 【继承】子类构造方法：通过 super() 调用父类构造方法，初始化继承来的属性
     * @param id       商品编号
     * @param name     商品名称
     * @param price    原价
     * @param discount 折扣力度，如 0.8 表示8折
     */
    public DiscountProduct(String id, String name, double price, double discount) {
        // 【继承】super 调用父类 Product 的构造方法，复用父类初始化逻辑
        super(id, name, price);
        this.discount = discount;
    }

    /**
     * 【多态】重写（Override）父类的 getPrice() 方法
     * 父类返回原价，子类返回 原价 × 折扣
     * 当用 Product 类型引用指向 DiscountProduct 对象时，调用 getPrice() 会执行此版本
     * @return 折后价格
     */
    @Override
    public double getPrice() {
        // getUnitPrice() 是从父类继承来的 getter，体现【继承】
        return getUnitPrice() * discount;
    }

    // ===== 子类新增属性的 getter / setter =====

    public double getDiscount() {
        return discount;
    }

    public void setDiscount(double discount) {
        this.discount = discount;
    }

    /**
     * 重写 toString，额外显示折扣信息
     */
    @Override
    public String toString() {
        return String.format("编号:%s | 名称:%s | 原价:%.2f | 折扣:%.1f折 | 实付:%.2f",
                getId(), getName(), getUnitPrice(), discount * 10, getPrice());
    }
}
