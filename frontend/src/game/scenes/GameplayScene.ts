import * as Phaser from 'phaser';

export class GameplayScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite;
  private obstacles!: Phaser.Physics.Arcade.Group;
  private goalZone!: Phaser.GameObjects.Zone;
  
  private score: number = 0;
  private startTime: number = 0;
  private gameStarted: boolean = false;
  
  // Difficulty config (MentalFlow Upgrade)
  private difficultyLevel: 'easy' | 'medium' | 'hard' = 'medium';
  private spawnRate: number = 0.04;
  private obstacleSpeed: number = 150;
  private playerSpeed: number = 300;
  private playerSize: number = 20; // Default radius
  private obstacleWind: number = 0; // Horizontal movement
  
  // Game state
  private isPaused: boolean = false;
  private isGameOver: boolean = false;
  
  // Input
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private keyW!: Phaser.Input.Keyboard.Key;
  private keyA!: Phaser.Input.Keyboard.Key;
  private keyS!: Phaser.Input.Keyboard.Key;
  private keyD!: Phaser.Input.Keyboard.Key;
  
  // UI
  private scoreText!: Phaser.GameObjects.Text;
  private timerText!: Phaser.GameObjects.Text;
  private difficultyBadge!: Phaser.GameObjects.Text;
  private reasoningText!: Phaser.GameObjects.Text;
  
  // Visuals
  private playerGlow!: Phaser.GameObjects.Arc;
  private bgGradient!: Phaser.GameObjects.Rectangle;

  constructor() {
    super('GameplayScene');
  }

  init(data: { difficulty?: 'easy' | 'medium' | 'hard' }) {
    this.difficultyLevel = data?.difficulty || this.registry?.get('difficulty') || 'medium';
    this.setDifficultyConfig();
    this.score = 0;
    this.isGameOver = false;
    this.isPaused = false;
    this.gameStarted = false;
  }

  private setDifficultyConfig() {
    const configs = {
      easy: {
        spawnRate: 0.02,
        obstacleSpeed: 120,
        playerSpeed: 350, // Faster player in easy for better control
        playerSize: 22,   // Larger hit radius
        obstacleWind: 0,
        theme: 0x0f172a,   // Deep blue
        accent: 0x10b981   // Green
      },
      medium: {
        spawnRate: 0.05,
        obstacleSpeed: 180,
        playerSpeed: 300,
        playerSize: 18,
        obstacleWind: 20,
        theme: 0x0f172a,
        accent: 0xf59e0b   // Amber
      },
      hard: {
        spawnRate: 0.12,   // Much denser
        obstacleSpeed: 280,
        playerSpeed: 250,  // Slower player = more precision needed
        playerSize: 14,    // Small target
        obstacleWind: 80,  // Strong erratic movement
        theme: 0x020617,   // Near black
        accent: 0xef4444   // Red
      },
    };

    const config = configs[this.difficultyLevel];
    this.spawnRate = config.spawnRate;
    this.obstacleSpeed = config.obstacleSpeed;
    this.playerSpeed = config.playerSpeed;
    this.playerSize = config.playerSize;
    this.obstacleWind = config.obstacleWind;
  }

  create() {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // ── Theme Colors ──
    const themes: Record<string, number> = { easy: 0x064e3b, medium: 0x1e1b4b, hard: 0x450a0a };
    const bgColors: Record<string, number> = { easy: 0x0f172a, medium: 0x0f172a, hard: 0x020617 };

    // ── Background ──
    this.bgGradient = this.add.rectangle(width / 2, height / 2, width, height, bgColors[this.difficultyLevel]);
    
    // Add a glowing aura at the top goal
    const goalAura = this.add.rectangle(width / 2, 50, width, 100, themes[this.difficultyLevel], 0.15);
    goalAura.setStrokeStyle(2, themes[this.difficultyLevel], 0.4);

    this.add.text(width / 2, 50, 'FOCUS: REACH THE CALM ZONE', {
      fontSize: '12px',
      color: '#ffffff',
      fontFamily: 'Inter, system-ui, sans-serif',
      letterSpacing: 2
    }).setOrigin(0.5).setAlpha(0.6);

    // ── Textures ──
    // Player
    const playerTex = this.make.graphics({ x: 0, y: 0, add: false });
    playerTex.fillStyle(0xffffff, 1);
    playerTex.fillCircle(25, 25, this.playerSize);
    playerTex.lineStyle(3, 0x6366f1, 0.8);
    playerTex.strokeCircle(25, 25, this.playerSize + 4);
    playerTex.generateTexture('player_tex', 50, 50);
    playerTex.destroy();

    // Obstacle
    const obsTex = this.make.graphics({ x: 0, y: 0, add: false });
    obsTex.fillStyle(0xffffff, 1);
    obsTex.fillRoundedRect(0, 0, 32, 32, 4);
    obsTex.generateTexture('obstacle_tex', 32, 32);
    obsTex.destroy();

    // ── Sprites ──
    this.player = this.physics.add.sprite(width / 2, height - 100, 'player_tex');
    this.player.setCollideWorldBounds(true);
    this.player.setCircle(this.playerSize, 25 - this.playerSize, 25 - this.playerSize);

    this.playerGlow = this.add.circle(this.player.x, this.player.y, this.playerSize + 10, 0x6366f1, 0.2);

    this.obstacles = this.physics.add.group();

    this.goalZone = this.add.zone(width / 2, 50, width, 100);
    this.physics.world.enable(this.goalZone, Phaser.Physics.Arcade.STATIC_BODY);

    // ── UI ──
    this.scoreText = this.add.text(24, 24, 'FLOW POINTS 0', {
      fontSize: '14px',
      color: '#cbd5e1',
      fontFamily: 'Inter, system-ui, sans-serif',
      fontStyle: 'bold'
    });

    this.timerText = this.add.text(width - 24, 24, '0s', {
      fontSize: '14px',
      color: '#cbd5e1',
      fontFamily: 'Inter, system-ui, sans-serif'
    }).setOrigin(1, 0);

    const statusColors: Record<string, string> = { easy: '#10b981', medium: '#f59e0b', hard: '#ef4444' };
    this.difficultyBadge = this.add.text(24, height - 24, `${this.difficultyLevel.toUpperCase()} PROTOCOL`, {
      fontSize: '10px',
      color: statusColors[this.difficultyLevel],
      fontFamily: 'Inter, system-ui, sans-serif',
      padding: { x: 8, y: 4 },
      backgroundColor: statusColors[this.difficultyLevel] + '22'
    }).setOrigin(0, 1);

    // ── Clinical Reasoning Text ──
    const reasonings: Record<string, string> = {
      easy: "CALM FLOW: Focus on steady movement and rhythmic breathing.",
      medium: "ADAPTIVE FLOW: Managing moderate external stimuli to build resilience.",
      hard: "INTENSIVE FLOW: High-challenge protocol to activate executive function."
    };
    this.reasoningText = this.add.text(width / 2, height - 60, reasonings[this.difficultyLevel], {
      fontSize: '11px',
      color: '#94a3b8',
      fontFamily: 'Inter, system-ui, sans-serif',
      fontStyle: 'italic'
    }).setOrigin(0.5).setAlpha(0);

    this.tweens.add({
      targets: this.reasoningText,
      alpha: 1,
      y: height - 80,
      duration: 1000,
      delay: 500,
      ease: 'Power2'
    });

    // ── Controls ──
    if (this.input.keyboard) {
      this.cursors = this.input.keyboard.createCursorKeys();
      this.keyW = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W);
      this.keyA = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A);
      this.keyS = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S);
      this.keyD = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D);
    }

    // ── Events ──
    this.physics.add.overlap(this.player, this.obstacles, this.hitObstacle, undefined, this);
    this.physics.add.overlap(this.player, this.goalZone, this.reachGoal, undefined, this);

    this.startTime = this.time.now;
    this.gameStarted = true;
  }

  update() {
    if (this.isGameOver || this.isPaused || !this.gameStarted) return;

    // Movement
    let vx = 0, vy = 0;
    if (this.cursors.left.isDown || this.keyA.isDown) vx = -this.playerSpeed;
    if (this.cursors.right.isDown || this.keyD.isDown) vx = this.playerSpeed;
    if (this.cursors.up.isDown || this.keyW.isDown) vy = -this.playerSpeed;
    if (this.cursors.down.isDown || this.keyS.isDown) vy = this.playerSpeed;
    this.player.setVelocity(vx, vy);

    this.playerGlow.setPosition(this.player.x, this.player.y);

    // Spawning
    if (Math.random() < this.spawnRate) {
      this.spawnObstacle();
    }

    // Clean up & score
    this.obstacles.getChildren().forEach((child) => {
      const obj = child as Phaser.Physics.Arcade.Sprite;
      if (obj.y > this.cameras.main.height + 50) {
        obj.destroy();
        this.score += (this.difficultyLevel === 'hard' ? 25 : (this.difficultyLevel === 'medium' ? 15 : 10));
        this.scoreText.setText(`FLOW POINTS ${this.score}`);
      }
    });

    // Timer
    const elapsed = Math.floor((this.time.now - this.startTime) / 1000);
    this.timerText.setText(`${elapsed}s`);
  }

  private spawnObstacle() {
    const x = Phaser.Math.Between(50, this.cameras.main.width - 50);
    const obstacle = this.obstacles.create(x, -50, 'obstacle_tex') as Phaser.Physics.Arcade.Sprite;
    
    obstacle.setTint(this.difficultyLevel === 'hard' ? 0xef4444 : (this.difficultyLevel === 'medium' ? 0xf59e0b : 0x64748b));
    obstacle.setVelocityY(this.obstacleSpeed + Phaser.Math.Between(-20, 20));
    
    // Wind effect in harder modes
    if (this.obstacleWind > 0) {
      obstacle.setVelocityX(Phaser.Math.Between(-this.obstacleWind, this.obstacleWind));
    }

    this.tweens.add({
      targets: obstacle,
      angle: 360,
      duration: 2000,
      repeat: -1
    });
  }

  private hitObstacle() {
    if (this.isGameOver) return;
    this.terminateGame(false);
  }

  private reachGoal() {
    if (this.isGameOver) return;
    this.terminateGame(true);
  }

  private terminateGame(success: boolean) {
    this.isGameOver = true;
    this.physics.pause();
    this.player.setTint(success ? 0x10b981 : 0xef4444);

    const duration = Math.floor((this.time.now - this.startTime) / 1000);
    
    // Emitted to GameContainer to trigger PostGameModal
    this.events.emit('gameEnded', {
      completed: success,
      score: this.score,
      duration,
      difficulty: this.difficultyLevel
    });
  }
}
