import java.util.Scanner;

/**
 * 测试主类
 * 模拟超市购物车结算的控制台交互
 */
public class Main {

    public static void main(String[] args) {

        // ===== 预先创建商品库（2个普通商品 + 2个打折商品）=====

        // 普通商品：调用 Product 构造方法
        Product p1 = new Product("P001", "可口可乐", 3.5);
        Product p2 = new Product("P002", "乐事薯片", 8.0);

        // 打折商品：调用 DiscountProduct 构造方法
        // 【多态】用父类 Product 引用指向子类 DiscountProduct 对象（向上转型）
        Product p3 = new DiscountProduct("D001", "蒙牛纯牛奶", 12.0, 0.8);  // 8折
        Product p4 = new DiscountProduct("D002", "奥利奥饼干", 15.0, 0.7);  // 7折

        // 将所有商品放入数组，方便按编号查找
        Product[] productCatalog = {p1, p2, p3, p4};

        // 创建购物车
        ShoppingCart cart = new ShoppingCart();

        Scanner scanner = new Scanner(System.in);

        // ===== 控制台菜单循环 =====
        while (true) {
            System.out.println();
            System.out.println("======== SmartCart 智能购物车 ========");
            System.out.println("1. 添加商品");
            System.out.println("2. 移除商品");
            System.out.println("3. 查看购物车");
            System.out.println("4. 结算并退出");
            System.out.print("请输入选项（1-4）：");

            int choice = scanner.nextInt();
            scanner.nextLine(); // 消费换行符

            switch (choice) {
                case 1:
                    // 添加商品：显示商品库，让用户选择编号
                    System.out.println("----- 可选商品 -----");
                    for (Product p : productCatalog) {
                        // 【多态】toString 自动区分普通商品和打折商品的显示格式
                        System.out.println(p);
                    }
                    System.out.print("请输入要添加的商品编号：");
                    String addId = scanner.nextLine();
                    boolean found = false;
                    for (Product p : productCatalog) {
                        if (p.getId().equals(addId)) {
                            // 【多态】addProduct 参数为 Product，传入普通或打折商品均可
                            cart.addProduct(p);
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        System.out.println("商品编号不存在！");
                    }
                    break;

                case 2:
                    // 移除商品
                    System.out.print("请输入要移除的商品编号：");
                    String removeId = scanner.nextLine();
                    cart.removeProduct(removeId);
                    break;

                case 3:
                    // 查看购物车
                    cart.showItems();
                    break;

                case 4:
                    // 结算并退出
                    if (cart.getItemCount() == 0) {
                        System.out.println("购物车为空，无需结算。");
                    } else {
                        cart.checkout();
                    }
                    System.out.println("感谢使用 SmartCart，再见！");
                    scanner.close();
                    return; // 结束程序

                default:
                    System.out.println("无效选项，请输入 1-4！");
            }
        }
    }
}
