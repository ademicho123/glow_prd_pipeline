# Glow Claims API - Production Dockerfile
# Multi-stage build for optimized image size

# === BUILD STAGE ===
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy project files
COPY ["src/*.csproj", "src/"]
COPY ["tests/*.csproj", "tests/"]

# Restore dependencies
RUN dotnet restore "src/Glow.Claims.Api.csproj"

# Copy source code
COPY src/ src/
COPY tests/ tests/

# Build
WORKDIR /src/src
RUN dotnet build -c Release -o /app/build

# === TEST STAGE ===
FROM build AS test
WORKDIR /src/tests
RUN dotnet test --no-restore --logger:trx

# === PUBLISH STAGE ===
FROM build AS publish
WORKDIR /src/src
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

# === RUNTIME STAGE ===
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Security: Run as non-root user
RUN addgroup --system --gid 1001 glowgroup && \
    adduser --system --uid 1001 --gid 1001 glowuser
USER glowuser

# Copy published app
COPY --from=publish /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Environment
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production
ENV DOTNET_RUNNING_IN_CONTAINER=true

EXPOSE 8080

ENTRYPOINT ["dotnet", "Glow.Claims.Api.dll"]
