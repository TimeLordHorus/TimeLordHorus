package com.sanctuary.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class GenerateModelResponse {
    private String generationId;
    private String status;
    private String modelUrl;
    private String thumbnailUrl;
    private Integer estimatedPolycount;
    private String createdAt;
}
