package com.itheima;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.Random;

/**
 * 简易贪吃蛇游戏
 * 使用方向键控制蛇的移动，吃到红色食物得分，撞墙或撞到自己游戏结束。
 */
public class SnakeGame extends JPanel implements ActionListener, KeyListener {
    // 游戏区域的大小（格子数）
    private static final int BOARD_WIDTH = 20;
    private static final int BOARD_HEIGHT = 20;
    // 每个格子的大小（像素）
    private static final int TILE_SIZE = 30;
    // 游戏计时器延迟（毫秒），控制蛇的移动速度
    private static final int DELAY = 200;

    // 蛇的身体，每个元素是一个坐标点（x, y）
    private final ArrayList<Point> snake;
    // 食物的坐标
    private Point food;
    // 蛇当前移动方向：0-上, 1-右, 2-下, 3-左
    private int direction;
    // 游戏是否结束
    private boolean gameOver;
    // 游戏计时器
    private Timer timer;
    // 随机数生成器
    private final Random random;

    public SnakeGame() {
        // 设置面板首选大小
        setPreferredSize(new Dimension(BOARD_WIDTH * TILE_SIZE, BOARD_HEIGHT * TILE_SIZE));
        setBackground(Color.BLACK);
        // 使面板可以获得键盘焦点
        setFocusable(true);
        addKeyListener(this);

        snake = new ArrayList<>();
        random = new Random();
        // 初始化游戏
        initGame();
    }

    /**
     * 初始化或重新开始游戏
     */
    private void initGame() {
        snake.clear();
        // 初始蛇身：3个格子，水平放置于中间偏左的位置
        int startX = BOARD_WIDTH / 2;
        int startY = BOARD_HEIGHT / 2;
        snake.add(new Point(startX, startY));
        snake.add(new Point(startX - 1, startY));
        snake.add(new Point(startX - 2, startY));

        direction = 1; // 初始向右移动
        gameOver = false;
        spawnFood();

        // 如果计时器已存在，则重新启动
        if (timer != null) {
            timer.stop();
        }
        timer = new Timer(DELAY, this);
        timer.start();
    }

    /**
     * 在地图空白处随机生成食物
     */
    private void spawnFood() {
        int x, y;
        do {
            x = random.nextInt(BOARD_WIDTH);
            y = random.nextInt(BOARD_HEIGHT);
            food = new Point(x, y);
        } while (snake.contains(food)); // 确保食物不生成在蛇身上
    }

    /**
     * 游戏逻辑更新（由计时器调用）
     */
    private void move() {
        if (gameOver) {
            return;
        }

        // 获取蛇头位置
        Point head = snake.get(0);
        // 计算新蛇头位置
        Point newHead = switch (direction) {
            case 0 -> new Point(head.x, head.y - 1); // 上
            case 1 -> new Point(head.x + 1, head.y); // 右
            case 2 -> new Point(head.x, head.y + 1); // 下
            case 3 -> new Point(head.x - 1, head.y); // 左
            default -> head;
        };

        // 碰撞检测：撞墙
        if (newHead.x < 0 || newHead.x >= BOARD_WIDTH ||
                newHead.y < 0 || newHead.y >= BOARD_HEIGHT) {
            gameOver = true;
            timer.stop();
            return;
        }

        // 碰撞检测：撞到自己（新蛇头不能与除尾部以外的蛇身重叠）
        // 注意：如果蛇没有吃到食物，尾部会移除，此时可以允许新头部与当前尾部重叠
        boolean ateFood = newHead.equals(food);
        if (!ateFood) {
            // 移除尾部（模拟移动）
            snake.remove(snake.size() - 1);
        }
        // 检查新头部是否与蛇身（已移除尾部）重叠
        if (snake.contains(newHead)) {
            gameOver = true;
            timer.stop();
            return;
        }

        // 将新头部插入到蛇身最前面
        snake.add(0, newHead);

        // 如果吃到食物，重新生成食物，蛇的长度已自动增加（因为没删尾部）
        if (ateFood) {
            spawnFood();
        }
    }

    /**
     * 绘制游戏画面
     */
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        if (gameOver) {
            // 游戏结束显示提示
            g.setColor(Color.RED);
            g.setFont(new Font("Arial", Font.BOLD, 24));
            String msg = "Game Over! press R restart";
            FontMetrics metrics = getFontMetrics(g.getFont());
            int x = (getWidth() - metrics.stringWidth(msg)) / 2;
            int y = getHeight() / 2;
            g.drawString(msg, x, y);
            return;
        }

        // 绘制网格线（可选，便于观察格子）
        g.setColor(Color.DARK_GRAY);
        for (int i = 0; i <= BOARD_WIDTH; i++) {
            g.drawLine(i * TILE_SIZE, 0, i * TILE_SIZE, BOARD_HEIGHT * TILE_SIZE);
        }
        for (int i = 0; i <= BOARD_HEIGHT; i++) {
            g.drawLine(0, i * TILE_SIZE, BOARD_WIDTH * TILE_SIZE, i * TILE_SIZE);
        }

        // 绘制食物
        g.setColor(Color.RED);
        g.fillRect(food.x * TILE_SIZE + 2, food.y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4);

        // 绘制蛇
        for (int i = 0; i < snake.size(); i++) {
            Point p = snake.get(i);
            if (i == 0) {
                // 蛇头颜色
                g.setColor(Color.GREEN.darker());
            } else {
                // 蛇身颜色
                g.setColor(Color.GREEN);
            }
            g.fillRect(p.x * TILE_SIZE + 2, p.y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4);
        }
    }

    /**
     * 计时器事件：每次触发时移动蛇并重绘
     */
    @Override
    public void actionPerformed(ActionEvent e) {
        move();
        repaint();
    }

    /**
     * 键盘按下事件处理
     */
    @Override
    public void keyPressed(KeyEvent e) {
        int key = e.getKeyCode();

        // 游戏结束时按 R 重新开始
        if (gameOver) {
            if (key == KeyEvent.VK_R) {
                initGame();
                repaint();
            }
            return;
        }

        // 方向控制：不允许直接掉头
        switch (key) {
            case KeyEvent.VK_UP:
                if (direction != 2) direction = 0; // 当前不是向下，才能向上
                break;
            case KeyEvent.VK_RIGHT:
                if (direction != 3) direction = 1;
                break;
            case KeyEvent.VK_DOWN:
                if (direction != 0) direction = 2;
                break;
            case KeyEvent.VK_LEFT:
                if (direction != 1) direction = 3;
                break;
        }
    }

    @Override
    public void keyReleased(KeyEvent e) {}
    @Override
    public void keyTyped(KeyEvent e) {}

    /**
     * 程序入口
     */
    public static void main(String[] args) {
        // 在事件调度线程中创建并显示 GUI
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("贪吃蛇");
            SnakeGame game = new SnakeGame();
            frame.add(game);
            frame.pack();
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setLocationRelativeTo(null); // 窗口居中
            frame.setResizable(false);
            frame.setVisible(true);
        });
    }
}