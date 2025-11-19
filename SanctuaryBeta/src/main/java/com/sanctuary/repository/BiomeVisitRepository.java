package com.sanctuary.repository;

import com.sanctuary.model.BiomeVisit;
import com.sanctuary.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface BiomeVisitRepository extends JpaRepository<BiomeVisit, Long> {
    List<BiomeVisit> findByUserOrderByVisitedAtDesc(User user);
    long countByUserAndBiomeName(User user, String biomeName);
}
