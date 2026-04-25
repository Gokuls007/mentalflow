import * as Phaser from 'phaser';

export class GameplayScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite;
  private obstacles!: Phaser.Physics.Arcade.Group;
  private goalZone!: Phaser.GameObjects.Zone;
  
  private score: number = 0;
  private startTime: number = 0;
  private gameStarted: boolean = false;
  
  // Difficulty config
  private difficultyLevel: 'easy' | 'medium' | 'hard' = 'medium';
  private spawnRate: number = 0.04;
  private obstacleSpeed: number = 150;
  
  // Game state
  private isPaused: boolean = false;
  private isGameOver: boolean = false;
  
  // Input — stored once in create(), read every frame in update()
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private keyW!: Phaser.Input.Keyboard.Key;
  private keyA!: Phaser.Input.Keyboard.Key;
  private keyS!: Phaser.Input.Keyboard.Key;
  private keyD!: Phaser.Input.Keyboard.Key;
  
  // UI
  private scoreText!: Phaser.GameObjects.Text;
  private timerText!: Phaser.GameObjects.Text;
  private difficultyBadge!: Phaser.GameObjects.Text;
  
  // Particles / visual
  private playerGlow!: Phaser.GameObjects.Arc;

  constructor() {
    super('GameplayScene');
  }

  init(data: { difficulty?: 'easy' | 'medium' | 'hard' }) {
    // Read from init data first, then from game registry (set in config.ts preBoot)
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
        obstacleSpeed: 100,
      },
      medium: {
        spawnRate: 0.04,
        obstacleSpeed: 150,
      },
      hard: {
        spawnRate: 0.07,
        obstacleSpeed: 220,
      },
    };

    const config = configs[this.difficultyLevel];
    this.spawnRate = config.spawnRate;
    this.obstacleSpeed = config.obstacleSpeed;
  }

  preload() {
    // Procedural graphics — no external assets needed
  }

  create() {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // ── Background ──
    this.add.rectangle(width / 2, height / 2, width, height, 0x0f172a);

    // Goal zone indicator (top area — subtle gradient bar)
    const goalBar = this.add.rectangle(width / 2, 50, width, 100, 0x10b981, 0.08);
    goalBar.setStrokeStyle(1, 0x10b981, 0.2);

    const goalLabel = this.add.text(width / 2, 50, '⬆ REACH THIS ZONE ⬆', {
      fontSize: '14px',
      color: '#10b981',
      fontFamily: 'Inter, system-ui, sans-serif',
    }).setOrigin(0.5).setAlpha(0.5);

    // ── Player texture (procedural) ──
    const playerTex = this.make.graphics({ x: 0, y: 0, add: false });
    playerTex.fillStyle(0x6366f1, 1);
    playerTex.fillCircle(25, 25, 20);
    // Outer glow ring
    playerTex.lineStyle(2, 0x818cf8, 0.6);
    playerTex.strokeCircle(25, 25, 24);
    playerTex.generateTexture('player_tex', 50, 50);
    playerTex.destroy();

    // ── Obstacle texture (procedural) ──
    const obsTex = this.make.graphics({ x: 0, y: 0, add: false });
    obsTex.fillStyle(0xf43f5e, 1);
    obsTex.fillRoundedRect(0, 0, 36, 36, 6);
    obsTex.generateTexture('obstacle_tex', 36, 36);
    obsTex.destroy();

    // ── Player sprite ──
    this.player = this.physics.add.sprite(width / 2, height - 100, 'player_tex');
    this.player.setCollideWorldBounds(true);

    // Player glow effect (decorative arc behind the sprite)
    this.playerGlow = this.add.circle(width / 2, height - 100, 30, 0x6366f1, 0.15);

    // ── Obstacles group ──
    this.obstacles = this.physics.add.group({
      defaultKey: 'obstacle_tex',
      maxSize: 50,
      runChildUpdate: false,
    });

    // ── Goal Zone (Phaser 4 compatible) ──
    // In Phaser 4, use this.add.zone + physics.world.enable
    this.goalZone = this.add.zone(width / 2, 50, width, 100);
    this.physics.world.enable(this.goalZone, Phaser.Physics.Arcade.STATIC_BODY);

    // ── HUD ──
    const hudStyle: Phaser.Types.GameObjects.Text.TextStyle = {
      fontSize: '20px',
      color: '#94a3b8',
      fontFamily: 'Inter, system-ui, sans-serif',
    };

    this.scoreText = this.add.text(24, 20, 'SCORE  0', {
      ...hudStyle,
      fontSize: '18px',
      color: '#e2e8f0',
    });

    this.timerText = this.add.text(width - 140, 20, '0s', {
      ...hudStyle,
      fontSize: '18px',
      color: '#e2e8f0',
    }).setOrigin(0, 0);

    const diffColors: Record<string, string> = {
      easy: '#10b981',
      medium: '#f59e0b',
      hard: '#ef4444',
    };
    this.difficultyBadge = this.add.text(24, height - 40, this.difficultyLevel.toUpperCase(), {
      fontSize: '11px',
      color: diffColors[this.difficultyLevel],
      fontFamily: 'Inter, system-ui, sans-serif',
      backgroundColor: diffColors[this.difficultyLevel] + '18',
      padding: { x: 10, y: 4 },
    });

    // ── Input setup (create keys ONCE here, read in update) ──
    if (this.input.keyboard) {
      this.cursors = this.input.keyboard.createCursorKeys();
      this.keyW = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W);
      this.keyA = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A);
      this.keyS = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S);
      this.keyD = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D);
      this.input.keyboard.on('keydown-ESC', () => this.togglePause());
    }

    // ── Pointer/touch support: player follows pointer when held ──
    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      if (pointer.isDown && !this.isGameOver && !this.isPaused && this.gameStarted) {
        this.physics.moveToObject(this.player, pointer, 300);
      }
    });
    this.input.on('pointerup', () => {
      if (!this.isGameOver && !this.isPaused) {
        this.player.setVelocity(0, 0);
      }
    });

    // ── Collisions ──
    this.physics.add.overlap(this.player, this.obstacles, this.hitObstacle, undefined, this);
    this.physics.add.overlap(this.player, this.goalZone, this.reachGoal, undefined, this);

    // ── Start game ──
    this.startTime = this.time.now;
    this.gameStarted = true;

    this.events.emit('gameStarted', { difficulty: this.difficultyLevel });
  }

  update(_time: number, _delta: number) {
    if (this.isGameOver || this.isPaused || !this.gameStarted) return;

    // ── Player movement (arrow keys + WASD) ──
    // Uses keys created once in create() — NOT recreated every frame
    if (this.cursors) {
      const speed = 300;
      let vx = 0;
      let vy = 0;

      if (this.cursors.left.isDown || this.keyA.isDown) vx = -speed;
      if (this.cursors.right.isDown || this.keyD.isDown) vx = speed;
      if (this.cursors.up.isDown || this.keyW.isDown) vy = -speed;
      if (this.cursors.down.isDown || this.keyS.isDown) vy = speed;

      // Only override velocity if a key is pressed (allow pointer movement otherwise)
      if (vx !== 0 || vy !== 0) {
        this.player.setVelocity(vx, vy);
      } else if (!this.input.activePointer.isDown) {
        // Stop if nothing is pressed
        this.player.setVelocity(0, 0);
      }
    }

    // Keep glow synced to player position
    this.playerGlow.setPosition(this.player.x, this.player.y);

    // ── Spawn obstacles ──
    if (Math.random() < this.spawnRate) {
      this.spawnObstacle();
    }

    // ── Cleanup off-screen obstacles + award points ──
    this.obstacles.getChildren().forEach((child) => {
      const obj = child as Phaser.Physics.Arcade.Sprite;
      if (obj.y > this.cameras.main.height + 40) {
        obj.destroy();
        this.score += 10;
        this.updateScoreDisplay();
      }
    });

    // ── Timer ──
    const elapsed = Math.floor((this.time.now - this.startTime) / 1000);
    this.timerText.setText(`${elapsed}s`);
  }

  private spawnObstacle() {
    const x = Phaser.Math.Between(40, this.cameras.main.width - 40);
    const obstacle = this.obstacles.create(x, -30, 'obstacle_tex') as Phaser.Physics.Arcade.Sprite;
    if (!obstacle) return; // maxSize reached

    obstacle.setVelocityY(this.obstacleSpeed);
    obstacle.setVelocityX(Phaser.Math.Between(-30, 30));

    // Slight rotation for visual variety
    this.tweens.add({
      targets: obstacle,
      angle: Phaser.Math.Between(-180, 180),
      duration: 3000,
      ease: 'Linear',
    });
  }

  private hitObstacle() {
    if (this.isGameOver) return;

    this.isGameOver = true;
    this.physics.pause();
    this.player.setTint(0xff0000);
    this.playerGlow.setFillStyle(0xff0000, 0.2);

    // Flash effect
    this.cameras.main.shake(200, 0.01);
    this.cameras.main.flash(300, 255, 50, 50, false);

    const duration = Math.floor((this.time.now - this.startTime) / 1000);

    // Show game-over text
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;
    this.add.text(width / 2, height / 2 - 30, 'OBSTACLE HIT', {
      fontSize: '32px',
      color: '#f43f5e',
      fontFamily: 'Inter, system-ui, sans-serif',
      fontStyle: 'bold',
    }).setOrigin(0.5);
    this.add.text(width / 2, height / 2 + 10, `Score: ${this.score}  •  Time: ${duration}s`, {
      fontSize: '16px',
      color: '#94a3b8',
      fontFamily: 'Inter, system-ui, sans-serif',
    }).setOrigin(0.5);

    this.events.emit('gameEnded', {
      completed: false,
      score: this.score,
      duration,
      difficulty: this.difficultyLevel,
    });
  }

  private reachGoal() {
    if (this.isGameOver) return;

    this.isGameOver = true;
    this.physics.pause();
    this.player.setTint(0x10b981);
    this.playerGlow.setFillStyle(0x10b981, 0.3);

    const duration = Math.floor((this.time.now - this.startTime) / 1000);

    // Show success text
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;
    this.add.text(width / 2, height / 2 - 30, '✓ GOAL REACHED', {
      fontSize: '32px',
      color: '#10b981',
      fontFamily: 'Inter, system-ui, sans-serif',
      fontStyle: 'bold',
    }).setOrigin(0.5);
    this.add.text(width / 2, height / 2 + 10, `Score: ${this.score}  •  Time: ${duration}s`, {
      fontSize: '16px',
      color: '#94a3b8',
      fontFamily: 'Inter, system-ui, sans-serif',
    }).setOrigin(0.5);

    this.events.emit('gameEnded', {
      completed: true,
      score: this.score,
      duration,
      difficulty: this.difficultyLevel,
    });
  }

  private togglePause() {
    if (this.isGameOver) return;

    this.isPaused = !this.isPaused;
    if (this.isPaused) {
      this.physics.pause();
      // Show pause overlay
      const w = this.cameras.main.width;
      const h = this.cameras.main.height;
      const overlay = this.add.rectangle(w / 2, h / 2, w, h, 0x000000, 0.6).setName('pauseOverlay');
      const txt = this.add.text(w / 2, h / 2, 'PAUSED\n\nPress ESC to resume', {
        fontSize: '28px',
        color: '#e2e8f0',
        fontFamily: 'Inter, system-ui, sans-serif',
        align: 'center',
      }).setOrigin(0.5).setName('pauseText');
    } else {
      this.physics.resume();
      // Remove pause overlay
      this.children.getByName('pauseOverlay')?.destroy();
      this.children.getByName('pauseText')?.destroy();
    }
  }

  private updateScoreDisplay() {
    this.scoreText.setText(`SCORE  ${this.score}`);
  }
}
