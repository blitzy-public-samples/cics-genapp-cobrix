******************************************************************
*  COPYBOOK  : GFORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : OR
******************************************************************
 01  RT-FOR-RATING.

          03 RT-FOR-TERRITORY-CODE            PIC X(3).
          03 RT-FOR-CLASS-CODE                PIC X(4).
          03 RT-FOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FOR-RATED-PREMIUM             PIC 9(9)V9(2).
