package com.itheima;

import java.util.Scanner;

public class LotteryGame {
    public static void main(String[] args) {
        /* 彩票中奖案例，生成一个7位的随机数表示彩票号码，键盘录入一个7位数表示用户购买的彩票
        判断用户输入的彩票号码是否和系统生成的彩票号码一致*/

        // 1.生成一个7位的随机数表示彩票号码
        int lotteryNumber = (int) (Math.random() * 10000000);

        // 2.键盘录入一个7位数表示用户购买的彩票
        Scanner sc = new Scanner(System.in);
        System.out.println("请输入用户购买的彩票号码：");
        int userNumber = sc.nextInt();
        System.out.println("用户购买的彩票号码为：" + userNumber);


        // 3.判断用户输入的彩票号码是否和系统生成的彩票号码一致
        if (userNumber == lotteryNumber) {
            System.out.println("恭喜用户中奖了！");
        } else {
            System.out.println("很遗憾，用户没有中奖。");
        }
        System.out.println("系统生成的彩票号码为：" + lotteryNumber);
    }
}