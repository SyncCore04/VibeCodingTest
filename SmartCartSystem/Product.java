/**
 * 商品父类
 * 【封装】将商品编号、名称、单价设为私有属性，通过 getter/setter 控制访问
 */
public class Product {

    // 【封装】私有属性：外部无法直接访问，必须通过公共方法间接操作
    private String id;       // 商品编号
    private String name;     // 商品名称
    private double price;    // 单价

    /**
     * 【封装】构造方法：创建对象时一次性初始化所有属性
     * @param id    商品编号
     * @param name  商品名称
     * @param price 单价
     */
    public Product(String id, String name, double price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }

    /**
     * 普通方法：返回商品单价
     * 此方法会在子类 DiscountProduct 中被重写，是【多态】的基础
     * @return 单价
     */
    public double getPrice() {
        return price;
    }

    // ===== 以下为 getter / setter，体现【封装】 =====

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public double getUnitPrice() {
        return price;
    }

    public void setUnitPrice(double price) {
        this.price = price;
    }

    /**
     * 重写 toString，方便打印商品信息
     */
    @Override
    public String toString() {
        return String.format("编号:%s | 名称:%s | 单价:%.2f | 实付:%.2f",
                id, name, price, getPrice());
    }
}
