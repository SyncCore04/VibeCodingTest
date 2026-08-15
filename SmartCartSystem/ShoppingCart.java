import java.util.ArrayList;

/**
 * 购物车类
 * 【多态】使用 ArrayList<Product> 存储商品，既能放普通 Product，也能放 DiscountProduct
 */
public class ShoppingCart {

    // 【封装】私有属性：商品列表，外部不能直接操作此集合
    // 【多态】元素类型声明为父类 Product，实际可以存入任意子类对象
    private ArrayList<Product> items;

    /**
     * 构造方法：初始化购物车（创建空的商品列表）
     */
    public ShoppingCart() {
        items = new ArrayList<>();
    }

    /**
     * 【封装】添加商品到购物车
     * 【多态】参数类型为 Product，既可传入普通 Product，也可传入 DiscountProduct
     * @param p 商品对象
     */
    public void addProduct(Product p) {
        items.add(p);
        System.out.println("已添加：" + p.getName());
    }

    /**
     * 【封装】根据商品编号移除商品
     * @param id 要移除的商品编号
     */
    public void removeProduct(String id) {
        boolean removed = false;
        // 遍历列表，找到编号匹配的商品并移除
        for (int i = 0; i < items.size(); i++) {
            if (items.get(i).getId().equals(id)) {
                System.out.println("已移除：" + items.get(i).getName());
                items.remove(i);
                removed = true;
                break; // 只移除第一个匹配项
            }
        }
        if (!removed) {
            System.out.println("未找到编号为 " + id + " 的商品");
        }
    }

    /**
     * 【封装】查看购物车中所有商品明细
     */
    public void showItems() {
        if (items.isEmpty()) {
            System.out.println("购物车为空");
            return;
        }
        System.out.println("===== 购物车明细 =====");
        // 【多态】调用 toString() 时，普通商品和打折商品会输出不同格式
        for (Product p : items) {
            System.out.println(p);
        }
        System.out.println("共 " + items.size() + " 件商品");
        System.out.println("======================");
    }

    /**
     * 【封装】计算购物车原始总价（未应用满减规则）
     * 【多态】遍历列表调用 getPrice()，普通商品返回原价，打折商品返回折后价
     *       JVM 根据对象实际类型自动选择对应版本的方法——这就是运行时多态
     * @return 原始总价
     */
    public double getTotalPrice() {
        double total = 0;
        for (Product p : items) {
            // 【多态】核心：p 可能是 Product 也可能是 DiscountProduct，
            //        但统一调用 getPrice()，结果由对象实际类型决定
            total += p.getPrice();
        }
        return total;
    }

    /**
     * 【封装】结算：计算总价并应用"智能满减规则"
     * 规则：商品总件数 >= 3 件时，整单再打 9.5 折；否则按原价结算
     * @return 最终应付金额
     */
    public double checkout() {
        double originalTotal = getTotalPrice();
        int count = items.size();

        System.out.println("===== 结算单 =====");
        System.out.printf("商品件数：%d 件%n", count);
        System.out.printf("原始总价：%.2f 元%n", originalTotal);

        double finalPrice;
        if (count >= 3) {
            // 满3件及以上，整单9.5折
            finalPrice = originalTotal * 0.95;
            System.out.println("满足满减规则（>=3件），整单9.5折！");
            System.out.printf("优惠金额：%.2f 元%n", originalTotal - finalPrice);
        } else {
            // 不足3件，按原价
            finalPrice = originalTotal;
            System.out.println("未满足满减规则（需>=3件），按原价结算");
        }

        System.out.printf("应付金额：%.2f 元%n", finalPrice);
        System.out.println("==================");
        return finalPrice;
    }

    /**
     * 获取当前商品件数（供外部查询）
     * @return 商品件数
     */
    public int getItemCount() {
        return items.size();
    }
}
