package com.example.usermanage.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.example.usermanage.entity.User;

public interface UserService extends IService<User> {

    Page<User> pageQuery(Integer current, Integer size, String keyword);
}
